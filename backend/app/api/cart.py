from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any
from app.db.database import get_db
from app.models.user import User
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.schemas.cart import CartResponse, CartItemCreate, CartItemUpdate
from app.api.deps import get_current_user

router = APIRouter()

def get_or_create_cart(db: Session, customer_id: int) -> Cart:
    cart = db.query(Cart).filter(Cart.customer_id == customer_id).first()
    if not cart:
        cart = Cart(customer_id=customer_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

@router.get("/", response_model=CartResponse)
def get_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    return get_or_create_cart(db, current_user.id)

@router.post("/items", response_model=CartResponse)
def add_item_to_cart(item_in: CartItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    cart = get_or_create_cart(db, current_user.id)
    product = db.query(Product).filter(Product.id == item_in.product_id).first()
    
    if not product or product.status != "ACTIVE":
        raise HTTPException(status_code=404, detail="Product not found or inactive")
        
    if item_in.quantity > product.available_quantity:
        raise HTTPException(status_code=400, detail=f"Only {product.available_quantity} items available")
        
    # Check "One Cart Belongs to One Farmer" rule
    if cart.shop_id is not None and cart.shop_id != product.shop_id:
        raise HTTPException(
            status_code=400, 
            detail="CART_CONFLICT: Your cart contains items from another farmer. Clear cart first."
        )
        
    # Set shop_id if cart is empty
    if cart.shop_id is None:
        cart.shop_id = product.shop_id
        db.add(cart)
        
    # Check if item already exists
    existing_item = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.product_id == product.id).first()
    if existing_item:
        if existing_item.quantity + item_in.quantity > product.available_quantity:
             raise HTTPException(status_code=400, detail=f"Cannot add more. Only {product.available_quantity} items available in total")
        existing_item.quantity += item_in.quantity
    else:
        new_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=item_in.quantity)
        db.add(new_item)
        
    db.commit()
    db.refresh(cart)
    return cart

@router.patch("/items/{item_id}", response_model=CartResponse)
def update_item_quantity(item_id: int, item_in: CartItemUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    cart = get_or_create_cart(db, current_user.id)
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
        
    if item_in.quantity > item.product.available_quantity:
        raise HTTPException(status_code=400, detail=f"Only {item.product.available_quantity} items available")
        
    item.quantity = item_in.quantity
    db.commit()
    db.refresh(cart)
    return cart

@router.delete("/items/{item_id}", response_model=CartResponse)
def remove_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    cart = get_or_create_cart(db, current_user.id)
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
        
    db.delete(item)
    
    # If this was the last item, reset shop_id
    if len(cart.items) == 1:
        cart.shop_id = None
        db.add(cart)
        
    db.commit()
    db.refresh(cart)
    return cart

@router.delete("/clear", response_model=CartResponse)
def clear_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    cart = get_or_create_cart(db, current_user.id)
    
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    cart.shop_id = None
    
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart
