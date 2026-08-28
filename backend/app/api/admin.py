from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Any
from app.db.database import get_db
from app.models.user import User
from app.models.shop import Shop
from app.models.product import Product
from app.models.order import Order
from app.schemas.user import UserResponse
from app.schemas.shop import ShopResponse
from app.schemas.product import ProductResponse
from app.api.deps import get_current_user
import calendar

router = APIRouter()

def verify_admin(current_user: User):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not enough permissions")

@router.get("/dashboard-stats")
def get_dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    verify_admin(current_user)
    
    total_customers = db.query(User).filter(User.role == "CUSTOMER").count()
    total_farmers = db.query(User).filter(User.role == "FARMER").count()
    total_shops = db.query(Shop).count()
    total_products = db.query(Product).count()
    
    # Orders exclude CANCELLED
    orders = db.query(Order).filter(Order.status != "CANCELLED").all()
    total_revenue = sum(order.total_amount for order in orders)
    total_orders = len(orders)
    
    # Sales by month (Current Year)
    sales_by_month = {}
    for order in orders:
        month = order.created_at.strftime("%b") # e.g. "Jan", "Feb"
        if month not in sales_by_month:
            sales_by_month[month] = 0
        sales_by_month[month] += order.total_amount
        
    # Format for Recharts
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_data = [{"name": month, "revenue": sales_by_month.get(month, 0)} for month in months]

    return {
        "total_customers": total_customers,
        "total_farmers": total_farmers,
        "total_shops": total_shops,
        "total_products": total_products,
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "monthly_revenue": monthly_data
    }


@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    verify_admin(current_user)
    users = db.query(User).all()
    return users

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    verify_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
        
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@router.get("/shops", response_model=List[ShopResponse])
def get_all_shops(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    verify_admin(current_user)
    shops = db.query(Shop).all()
    return shops

@router.patch("/shops/{shop_id}/status", response_model=ShopResponse)
def update_shop_status(shop_id: int, status: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    verify_admin(current_user)
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
        
    if status not in ["ACTIVE", "INACTIVE", "PENDING"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    shop.status = status
    db.add(shop)
    db.commit()
    db.refresh(shop)
    return shop

@router.patch("/users/{user_id}/status", response_model=UserResponse)
def update_user_status(user_id: int, is_active: bool, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    verify_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
        
    user.is_active = is_active
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/products", response_model=List[ProductResponse])
def get_all_products(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    verify_admin(current_user)
    products = db.query(Product).all()
    return products

@router.patch("/products/{product_id}/status", response_model=ProductResponse)
def update_product_status(product_id: int, status: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    verify_admin(current_user)
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    if status not in ["ACTIVE", "INACTIVE"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    product.status = status
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
