from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str
    phone_number: str | None = None
    address: str | None = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: str | None = None
    phone_number: str | None = None
    address: str | None = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None
