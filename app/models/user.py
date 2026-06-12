"""
Database Models - Users and Authentication
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.core.database import Base

class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    FARMER = "farmer"
    BUYER = "buyer"
    TRANSPORTER = "transporter"
    AGRO_DEALER = "agro_dealer"

class User(Base):
    """User Model"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(String(50), default=UserRole.FARMER, nullable=False)
    is_verified = Column(Boolean, default=False)
    
    region = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    
    average_rating = Column(Float, default=0.0)
    total_ratings = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User {self.phone_number}>"