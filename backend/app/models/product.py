from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    name = Column(String, index=True, nullable=False)
    category = Column(String, index=True)
    description = Column(Text)
    price = Column(Float, nullable=False)
    available_quantity = Column(Integer, nullable=False, default=0)
    image_url = Column(String)
    status = Column(String, default="ACTIVE") # ACTIVE, INACTIVE
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    shop = relationship("Shop", back_populates="products")
