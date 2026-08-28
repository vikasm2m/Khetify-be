from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.product import ProductResponse

class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(CartItemBase):
    id: int
    product: ProductResponse
    
    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    id: int
    shop_id: Optional[int]
    items: List[CartItemResponse]
    
    class Config:
        from_attributes = True
