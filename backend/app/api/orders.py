from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List
from app.db.database import get_db
from app.models.user import User
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.schemas.order import OrderResponse
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[OrderResponse])
def get_my_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    """Get all orders for the current customer."""
    orders = db.query(Order).filter(Order.customer_id == current_user.id).order_by(Order.created_at.desc()).all()
    return orders

@router.post("/checkout", response_model=OrderResponse)
def checkout(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    cart = db.query(Cart).filter(Cart.customer_id == current_user.id).first()
    
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
        
    shop_id = cart.shop_id
    total_amount = 0.0
    
    # Verify stock and calculate total before starting transaction
    for item in cart.items:
        # Re-fetch product with lock to ensure stock safety (in real world)
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product or product.status != "ACTIVE":
             raise HTTPException(status_code=400, detail=f"Product {item.product.name} is no longer available")
             
        if item.quantity > product.available_quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")
            
        total_amount += (product.price * item.quantity)
        
    try:
        # 1. Create Order
        order = Order(
            customer_id=current_user.id,
            shop_id=shop_id,
            total_amount=total_amount
        )
        db.add(order)
        db.flush() # get order.id
        
        # 2. Create OrderItems & Reduce Stock
        for item in cart.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            
            # Reduce stock
            product.available_quantity -= item.quantity
            db.add(product)
            
            # Create order item
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                price=product.price,
                quantity=item.quantity,
                subtotal=product.price * item.quantity
            )
            db.add(order_item)
            
        # 3. Clear Cart safely by deleting items from session
        for item in cart.items:
            db.delete(item)
            
        cart.shop_id = None
        db.add(cart)
        
        # COMMIT everything
        db.commit()
        db.refresh(order)
        return order
        
    except Exception as e:
        db.rollback()
        print(f"Checkout error: {e}")
        raise HTTPException(status_code=500, detail="Checkout failed. Try again.")
