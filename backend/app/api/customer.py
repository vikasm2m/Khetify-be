from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Any, Optional
from app.db.database import get_db
from app.models.shop import Shop
from app.models.product import Product
from app.models.user import User
from app.schemas.shop import ShopResponse
from app.schemas.product import ProductResponse

router = APIRouter()

@router.get("/shops", response_model=List[ShopResponse])
def get_shops(db: Session = Depends(get_db)) -> Any:
    # Only active shops and active farmers
    shops = db.query(Shop).join(User, Shop.farmer_id == User.id).filter(
        Shop.status == "ACTIVE",
        User.is_active == True
    ).all()
    return shops

@router.get("/shops/{shop_id}", response_model=ShopResponse)
def get_shop_details(shop_id: int, db: Session = Depends(get_db)) -> Any:
    shop = db.query(Shop).join(User, Shop.farmer_id == User.id).filter(
        Shop.id == shop_id, 
        Shop.status == "ACTIVE",
        User.is_active == True
    ).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    return shop

@router.get("/shops/{shop_id}/products", response_model=List[ProductResponse])
def get_shop_products(shop_id: int, db: Session = Depends(get_db)) -> Any:
    shop = db.query(Shop).join(User, Shop.farmer_id == User.id).filter(
        Shop.id == shop_id, 
        Shop.status == "ACTIVE",
        User.is_active == True
    ).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
        
    products = db.query(Product).filter(Product.shop_id == shop.id, Product.status == "ACTIVE").all()
    return products

@router.get("/products", response_model=List[ProductResponse])
def get_products(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search term for product name"),
    category: Optional[str] = Query(None, description="Filter by category")
) -> Any:
    query = db.query(Product).join(Shop).join(User, Shop.farmer_id == User.id).filter(
        Product.status == "ACTIVE",
        Shop.status == "ACTIVE",
        User.is_active == True
    )
    
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
        
    products = query.all()
    return products

@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product_details(product_id: int, db: Session = Depends(get_db)) -> Any:
    product = db.query(Product).join(Shop).join(User, Shop.farmer_id == User.id).filter(
        Product.id == product_id,
        Product.status == "ACTIVE",
        Shop.status == "ACTIVE",
        User.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
