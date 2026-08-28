from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Any
from app.db.database import get_db
from app.models.user import User
from app.models.shop import Shop
from app.schemas.user import UserResponse
from app.schemas.shop import ShopResponse
from app.api.deps import get_current_user

router = APIRouter()

def verify_admin(current_user: User):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not enough permissions")

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
