"""
Database Models - Logistics and Verification
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, Enum, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.core.database import Base

class TransportStatus(str, enum.Enum):
    """Transport request status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class TransportRequest(Base):
    """Logistics/Transport Request"""
    __tablename__ = "transport_requests"
    
    id = Column(String(36), primary_key=True, index=True)
    requester_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    driver_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    
    # Shipment Details
    shipment_type = Column(String(50), nullable=False)  # crops, livestock, general
    cargo_description = Column(Text, nullable=False)
    cargo_weight_kg = Column(Float, nullable=True)
    cargo_value = Column(Float, nullable=True)
    
    # Locations
    pickup_location = Column(String(200), nullable=False)
    pickup_latitude = Column(Float, nullable=True)
    pickup_longitude = Column(Float, nullable=True)
    
    delivery_location = Column(String(200), nullable=False)
    delivery_latitude = Column(Float, nullable=True)
    delivery_longitude = Column(Float, nullable=True)
    
    # Transport
    vehicle_type = Column(String(50), nullable=False)  # motorcycle, bajaj, pickup, truck
    distance_km = Column(Float, nullable=True)
    estimated_cost = Column(Float, nullable=False)
    actual_cost = Column(Float, nullable=True)
    currency = Column(String(3), default="TZS")
    
    # Schedule
    pickup_date = Column(DateTime(timezone=True), nullable=False)
    expected_delivery_date = Column(DateTime(timezone=True), nullable=True)
    actual_delivery_date = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    status = Column(String(50), default=TransportStatus.PENDING)
    
    # Insurance
    requires_insurance = Column(Boolean, default=False)
    insurance_amount = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    requester = relationship("User", foreign_keys=[requester_id])
    driver = relationship("User", foreign_keys=[driver_id])
    tracking = relationship("ShipmentTracking", back_populates="transport")
    
    def __repr__(self):
        return f"<TransportRequest {self.id}>"

class ShipmentTracking(Base):
    """Real-time Shipment Tracking"""
    __tablename__ = "shipment_tracking"
    
    id = Column(String(36), primary_key=True, index=True)
    transport_id = Column(String(36), ForeignKey("transport_requests.id"), nullable=False, index=True)
    
    # Location
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    location_description = Column(String(200), nullable=True)
    
    # Status Update
    status = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    
    # Estimated Arrival
    estimated_arrival = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamp
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    transport = relationship("TransportRequest", back_populates="tracking")

class VerificationReport(Base):
    """User Verification Reports (KYC)"""
    __tablename__ = "verification_reports"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Verification Details
    verification_type = Column(String(50), nullable=False)  # kyc, phone, email, business
    status = Column(String(50), default="pending")  # pending, approved, rejected
    
    # Documents
    document_type = Column(String(50), nullable=True)  # national_id, passport, business_license
    document_front = Column(String(500), nullable=True)
    document_back = Column(String(500), nullable=True)
    document_number = Column(String(100), nullable=True)
    
    # Verification Process
    verified_by = Column(String(100), nullable=True)  # admin name
    verification_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Dates
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User")

class Rating(Base):
    """User Ratings and Reviews"""
    __tablename__ = "ratings"
    
    id = Column(String(36), primary_key=True, index=True)
    rater_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    rated_user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=True)
    
    # Rating
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review = Column(Text, nullable=True)
    
    # Categories
    quality_rating = Column(Integer, nullable=True)  # 1-5
    delivery_rating = Column(Integer, nullable=True)  # 1-5
    communication_rating = Column(Integer, nullable=True)  # 1-5
    
    # Responses
    seller_response = Column(Text, nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    rater = relationship("User", foreign_keys=[rater_id])
    rated_user = relationship("User", foreign_keys=[rated_user_id])

class Notification(Base):
    """User Notifications"""
    __tablename__ = "notifications"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Notification Details
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # order, payment, loan, market, alert
    
    # Content
    related_id = Column(String(36), nullable=True)  # order_id, loan_id, etc.
    action_url = Column(String(500), nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    
    # Channels
    send_push = Column(Boolean, default=True)
    send_sms = Column(Boolean, default=False)
    send_email = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)