from pydantic import BaseModel
from datetime import datetime

class ShopBase(BaseModel):
    name: str
    description: str | None = None
    address: str | None = None
    image_url: str | None = None

class ShopCreate(ShopBase):
    pass

class ShopUpdate(ShopBase):
    status: str | None = None

class ShopResponse(ShopBase):
    id: int
    farmer_id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
