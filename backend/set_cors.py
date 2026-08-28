import boto3
from app.core.config import settings

def set_cors():
    s3_client = boto3.client(
        's3',
        endpoint_url=settings.AWS_ENDPOINT_URL_S3,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
        config=boto3.session.Config(signature_version='s3v4', s3={'addressing_style': 'path'})
    )
    
    cors_configuration = {
        'CORSRules': [{
            'AllowedHeaders': ['*'],
            'AllowedMethods': ['GET', 'PUT', 'POST', 'HEAD', 'DELETE'],
            'AllowedOrigins': ['*'],
            'ExposeHeaders': ['ETag']
        }]
    }
    
    try:
        s3_client.create_bucket(Bucket='assets')
        print("Bucket 'assets' created successfully.")
    except Exception as e:
        print("Note: Bucket creation failed (it might already exist).", e)

    try:
        s3_client.put_bucket_cors(
            Bucket='assets',
            CORSConfiguration=cors_configuration
        )
        print("Successfully updated CORS policy on the 'assets' bucket.")
    except Exception as e:
        print("Failed to update CORS policy:", e)

if __name__ == "__main__":
    set_cors()
