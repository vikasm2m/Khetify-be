import uuid
import boto3
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from botocore.exceptions import ClientError
from app.api.deps import get_current_user
from app.models.user import User
from app.core.config import settings

router = APIRouter()

class PresignedUrlRequest(BaseModel):
    filename: str
    content_type: str

class PresignedUrlResponse(BaseModel):
    upload_url: str
    public_url: str

def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=settings.AWS_ENDPOINT_URL_S3,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
        config=boto3.session.Config(
            signature_version='s3v4',
            s3={'addressing_style': 'path'}
        )
    )

@router.post("/presigned-url", response_model=PresignedUrlResponse)
def generate_presigned_url(request: PresignedUrlRequest, current_user: User = Depends(get_current_user)):
    # Only authenticated users can upload
    s3_client = get_s3_client()
    bucket_name = "assets"
    
    # Generate a unique object key to prevent collisions
    ext = request.filename.split('.')[-1] if '.' in request.filename else 'bin'
    object_key = f"uploads/{current_user.id}/{uuid.uuid4()}.{ext}"
    
    try:
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_key,
                'ContentType': request.content_type
            },
            ExpiresIn=3600
        )
    except ClientError as e:
        raise HTTPException(status_code=500, detail="Could not generate presigned URL")
        
    # Public URL structure based on the provided endpoint and bucket (assuming forcePathStyle / bucket-in-path or subdomain)
    # Since it's Neon/S3 compatible storage, the public URL is usually <endpoint>/<bucket>/<key>
    public_url = f"{settings.AWS_ENDPOINT_URL_S3}/{bucket_name}/{object_key}"
    
    return PresignedUrlResponse(
        upload_url=presigned_url,
        public_url=public_url
    )
