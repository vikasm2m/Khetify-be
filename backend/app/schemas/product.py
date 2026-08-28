from pydantic import BaseModel
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    category: str | None = None
    description: str | None = None
    price: float
    available_quantity: int
    image_url: str | None = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    status: str | None = None

class ProductResponse(ProductBase):
    id: int
    shop_id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
