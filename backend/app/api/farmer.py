from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Any
from app.db.database import get_db
from app.models.user import User
from app.models.shop import Shop
from app.models.product import Product
from app.models.order import Order
from app.schemas.shop import ShopCreate, ShopUpdate, ShopResponse
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.schemas.order import OrderResponse
from app.api.deps import get_current_farmer
from pydantic import BaseModel

router = APIRouter()

# --- SHOP APIs ---

@router.get("/shop", response_model=ShopResponse)
def get_my_shop(db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)) -> Any:
    shop = db.query(Shop).filter(Shop.farmer_id == current_user.id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    return shop

@router.post("/shop", response_model=ShopResponse)
def create_shop(shop_in: ShopCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)) -> Any:
    existing_shop = db.query(Shop).filter(Shop.farmer_id == current_user.id).first()
    if existing_shop:
        raise HTTPException(status_code=400, detail="Farmer already has a shop")
    
    shop = Shop(**shop_in.dict(), farmer_id=current_user.id)
    db.add(shop)
    db.commit()
    db.refresh(shop)
    return shop

@router.put("/shop", response_model=ShopResponse)
def update_shop(shop_in: ShopUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)) -> Any:
    shop = db.query(Shop).filter(Shop.farmer_id == current_user.id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    update_data = shop_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(shop, field, value)
    
    db.add(shop)
    db.commit()
    db.refresh(shop)
    return shop


# --- PRODUCT APIs ---

@router.get("/products", response_model=List[ProductResponse])
def list_my_products(db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)) -> Any:
    shop = db.query(Shop).filter(Shop.farmer_id == current_user.id).first()
    if not shop:
        return []
    products = db.query(Product).filter(Product.shop_id == shop.id).all()
    return products

@router.post("/products", response_model=ProductResponse)
def create_product(product_in: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)) -> Any:
    shop = db.query(Shop).filter(Shop.farmer_id == current_user.id).first()
    if not shop:
        raise HTTPException(status_code=400, detail="You must create a shop first")
    
    product = Product(**product_in.dict(), shop_id=shop.id)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product_in: ProductUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)) -> Any:
    shop = db.query(Shop).filter(Shop.farmer_id == current_user.id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
        
    product = db.query(Product).filter(Product.id == product_id, Product.shop_id == shop.id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    update_data = product_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
        
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)) -> Any:
    shop = db.query(Shop).filter(Shop.farmer_id == current_user.id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
        
    product = db.query(Product).filter(Product.id == product_id, Product.shop_id == shop.id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}

@router.patch("/products/{product_id}/status", response_model=ProductResponse)
def update_product_status(product_id: int, status: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)) -> Any:
    shop = db.query(Shop).filter(Shop.farmer_id == current_user.id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
        
    product = db.query(Product).filter(Product.id == product_id, Product.shop_id == shop.id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    if status not in ["ACTIVE", "INACTIVE"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    product.status = status
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

# --- ORDER APIs ---

@router.get("/orders", response_model=List[OrderResponse])
def get_shop_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)) -> Any:
    shop = db.query(Shop).filter(Shop.farmer_id == current_user.id).first()
    if not shop:
        return []
    orders = db.query(Order).filter(Order.shop_id == shop.id).order_by(Order.created_at.desc()).all()
    return orders

from datetime import datetime

class MonthlyData(BaseModel):
    name: str
    earnings: float
    orders: int

class DashboardStatsResponse(BaseModel):
    total_orders: int
    total_earnings: float
    annual_income: float
    monthly_data: List[MonthlyData]

@router.get("/dashboard-stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)) -> Any:
    shop = db.query(Shop).filter(Shop.farmer_id == current_user.id).first()
    if not shop:
        return DashboardStatsResponse(total_orders=0, total_earnings=0, annual_income=0, monthly_data=[])
        
    orders = db.query(Order).filter(Order.shop_id == shop.id).all()
    
    total_orders = len(orders)
    total_earnings = 0.0
    annual_income = 0.0
    
    current_year = datetime.now().year
    
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_stats = {month: {"earnings": 0.0, "orders": 0} for month in months}
    
    for order in orders:
        if order.status != "CANCELLED":
            total_earnings += order.total_amount
            if order.created_at.year == current_year:
                annual_income += order.total_amount
                month_name = months[order.created_at.month - 1]
                monthly_stats[month_name]["earnings"] += order.total_amount
                monthly_stats[month_name]["orders"] += 1
                
    monthly_data = [
        MonthlyData(name=month, earnings=stats["earnings"], orders=stats["orders"])
        for month, stats in monthly_stats.items()
    ]
    
    return DashboardStatsResponse(
        total_orders=total_orders,
        total_earnings=total_earnings,
        annual_income=annual_income,
        monthly_data=monthly_data
    )

class OrderStatusUpdate(BaseModel):
    status: str

@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(order_id: int, status_update: OrderStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_farmer)) -> Any:
    shop = db.query(Shop).filter(Shop.farmer_id == current_user.id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
        
    order = db.query(Order).filter(Order.id == order_id, Order.shop_id == shop.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    valid_statuses = ["PENDING", "COMPLETED", "SHIPPED", "CANCELLED"]
    if status_update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    order.status = status_update.status
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
