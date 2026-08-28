from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, farmer, customer, cart, orders, admin, upload

app = FastAPI(title="FarmConnect API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(farmer.router, prefix="/api/v1/farmer", tags=["farmer"])
app.include_router(customer.router, prefix="/api/v1", tags=["customer"])
app.include_router(cart.router, prefix="/api/v1/cart", tags=["cart"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(upload.router, prefix="/api/v1/upload", tags=["upload"])

@app.get("/")
def read_root():
    return {"message": "Welcome to FarmConnect API"}
