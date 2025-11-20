from sqlalchemy import Column, Integer, String, Boolean, Float, Text
from .database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    event_type = Column(String, default="import_completed")
    is_active = Column(Boolean, default=True)