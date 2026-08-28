from pydantic import BaseModel
from typing import List
from datetime import datetime

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    price: float
    quantity: int
    subtotal: float
    
    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    customer_id: int
    shop_id: int
    total_amount: float
    status: str
    created_at: datetime
    items: List[OrderItemResponse]
    
    class Config:
        from_attributes = True
