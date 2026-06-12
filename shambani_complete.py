#!/usr/bin/env python3
"""
SHAMBANI LINK - COMPLETE APPLICATION
Kwa file hii moja, unaweza kuwa na mfumo kamili!

Usage:
  python3 shambani_complete.py

Then visit: http://localhost:8000/api/docs
"""

import os
import sys
import uuid
import logging
import json
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import enum

# FastAPI imports
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Database imports
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Integer, Float, ForeignKey, Text, JSON, Numeric, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

# Security imports
from passlib.context import CryptContext
from jose import JWTError, jwt
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================
# 1. DATABASE CONFIGURATION
# ============================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/shambani_link"
)

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600,
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

Base = declarative_base()

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================
# 2. SECURITY CONFIGURATION
# ============================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

class TokenManager:
    """JWT Token Management"""
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None

class PasswordManager:
    """Password Management"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)

class OTPManager:
    """OTP Management"""
    
    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """Generate OTP"""
        return ''.join(secrets.choice(string.digits) for _ in range(length))

class SecurityUtils:
    """Security Utilities"""
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate phone number"""
        phone = ''.join(filter(str.isdigit, phone))
        return 10 <= len(phone) <= 15
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

# ============================================================
# 3. DATABASE MODELS
# ============================================================

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    FARMER = "farmer"
    BUYER = "buyer"
    TRANSPORTER = "transporter"

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_VERIFICATION = "pending_verification"

class User(Base):
    """User Model"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    profile_picture = Column(String(500), nullable=True)
    
    role = Column(String(50), default=UserRole.FARMER, nullable=False)
    status = Column(String(50), default=UserStatus.PENDING_VERIFICATION)
    is_verified = Column(Boolean, default=False)
    is_phone_verified = Column(Boolean, default=False)
    
    region = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    
    average_rating = Column(Float, default=0.0)
    total_ratings = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    crops = relationship("Crop", back_populates="user")
    livestock = relationship("Livestock", back_populates="user")
    loans = relationship("LoanApplication", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")

class OTPRecord(Base):
    """OTP Storage"""
    __tablename__ = "otp_records"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    phone_number = Column(String(20), nullable=False)
    otp_code = Column(String(10), nullable=False)
    otp_type = Column(String(50), nullable=False)
    is_used = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)

class Crop(Base):
    """Crop Model"""
    __tablename__ = "crops"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    crop_name = Column(String(100), nullable=False)
    crop_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    
    quantity_kg = Column(Float, nullable=False)
    available_quantity_kg = Column(Float, nullable=False)
    price_per_kg = Column(Float, nullable=False)
    currency = Column(String(3), default="TZS")
    
    grade = Column(String(50), nullable=True)
    harvest_date = Column(DateTime(timezone=True), nullable=True)
    
    region = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    
    status = Column(String(50), default="available")
    images = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="crops")

class Livestock(Base):
    """Livestock Model"""
    __tablename__ = "livestock"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    animal_type = Column(String(50), nullable=False)
    breed = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    
    quantity = Column(Integer, nullable=False)
    available_quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Float, nullable=False)
    currency = Column(String(3), default="TZS")
    
    age_months = Column(Integer, nullable=True)
    weight_kg = Column(Float, nullable=True)
    health_status = Column(String(50), nullable=True)
    
    region = Column(String(100), nullable=True)
    status = Column(String(50), default="available")
    images = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="livestock")

class Order(Base):
    """Order Model"""
    __tablename__ = "orders"
    
    id = Column(String(36), primary_key=True, index=True)
    crop_id = Column(String(36), ForeignKey("crops.id"), nullable=True)
    
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    currency = Column(String(3), default="TZS")
    
    buyer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    seller_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    status = Column(String(50), default="pending")
    payment_status = Column(String(50), default="pending")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class LoanApplication(Base):
    """Loan Application Model"""
    __tablename__ = "loan_applications"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    loan_type = Column(String(50), nullable=False)
    loan_amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="TZS")
    interest_rate = Column(Float, nullable=False)
    loan_duration_months = Column(Integer, nullable=False)
    
    purpose = Column(Text, nullable=False)
    credit_score = Column(Float, nullable=True)
    status = Column(String(50), default="pending")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="loans")

class Transaction(Base):
    """Transaction Model"""
    __tablename__ = "transactions"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    transaction_type = Column(String(50), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="TZS")
    
    payment_method = Column(String(50), nullable=False)
    status = Column(String(50), default="pending")
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User", back_populates="transactions")

# ============================================================
# 4. SERVICES
# ============================================================

class AIHealthDiagnostics:
    """AI Health Diagnostics"""
    
    def __init__(self):
        self.diseases = {
            "crops": {
                "early_blight": {
                    "name": "Early Blight",
                    "symptoms": ["brown spots", "yellowing leaves"],
                    "treatment": ["fungicide", "remove infected leaves"]
                },
                "powdery_mildew": {
                    "name": "Powdery Mildew",
                    "symptoms": ["white powder", "curled leaves"],
                    "treatment": ["sulfur spray", "neem oil"]
                }
            },
            "livestock": {
                "mastitis": {
                    "name": "Mastitis",
                    "symptoms": ["swollen udder", "abnormal milk"],
                    "treatment": ["antibiotics", "clean milking"]
                },
                "pneumonia": {
                    "name": "Respiratory Disease",
                    "symptoms": ["coughing", "nasal discharge"],
                    "treatment": ["antibiotics", "ventilation"]
                }
            }
        }
    
    async def diagnose_crop(self, symptoms: List[str]) -> Dict[str, Any]:
        """Diagnose crop disease"""
        matching = []
        for disease_key, info in self.diseases["crops"].items():
            matched = [s for s in symptoms if any(kw in s.lower() for kw in info["symptoms"])]
            if matched:
                matching.append({
                    "disease": info["name"],
                    "confidence": len(matched) / len(info["symptoms"]),
                    "treatment": info["treatment"]
                })
        matching.sort(key=lambda x: x["confidence"], reverse=True)
        return {"status": "success", "diagnoses": matching[:3]}
    
    async def diagnose_livestock(self, symptoms: List[str]) -> Dict[str, Any]:
        """Diagnose livestock disease"""
        matching = []
        for disease_key, info in self.diseases["livestock"].items():
            matched = [s for s in symptoms if any(kw in s.lower() for kw in info["symptoms"])]
            if matched:
                matching.append({
                    "disease": info["name"],
                    "confidence": len(matched) / len(info["symptoms"]),
                    "treatment": info["treatment"]
                })
        matching.sort(key=lambda x: x["confidence"], reverse=True)
        return {"status": "success", "diagnoses": matching[:3]}

class CreditScorer:
    """Credit Scoring Service"""
    
    @staticmethod
    async def calculate_credit_score(user_id: str, db: Session) -> Dict[str, Any]:
        """Calculate credit score"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "error", "message": "User not found"}
        
        score = 300
        
        if user.is_verified:
            score += 150
        if user.is_phone_verified:
            score += 75
        
        if user.average_rating > 4.5:
            score += 150
        elif user.average_rating > 3.0:
            score += 50
        
        if score >= 900:
            tier = "EXCELLENT"
            max_loan = 10000000
            interest_rate = 8.0
        elif score >= 750:
            tier = "GOOD"
            max_loan = 5000000
            interest_rate = 12.0
        elif score >= 600:
            tier = "FAIR"
            max_loan = 2000000
            interest_rate = 15.0
        else:
            tier = "POOR"
            max_loan = 500000
            interest_rate = 18.0
        
        return {
            "status": "success",
            "credit_score": score,
            "credit_tier": tier,
            "max_loan_amount": max_loan,
            "interest_rate": interest_rate
        }

class USSDService:
    """USSD Service"""
    
    MAIN_MENU = """
Karibu Shambani Link
1. Bei za Soko
2. Uza Mazao
3. Uza Mifugo
4. Omba Mkopo
5. Omba Usafiri
6. Bima
7. Malipo
0. Rudi
"""
    
    async def handle_ussd(self, phone: str, text: str) -> str:
        """Handle USSD request"""
        if not text:
            return "CON " + self.MAIN_MENU
        
        choice = text.split("*")[-1] if text else ""
        
        if choice == "1":
            return "END Bei za mahindi: TZS 820/kg\nWali: TZS 1200/kg"
        elif choice == "2":
            return "CON Jina la mazao:"
        elif choice == "3":
            return "CON Aina ya mifugo:"
        elif choice == "0":
            return "END Asante!"
        else:
            return "CON " + self.MAIN_MENU

class PaymentGateway:
    """Payment Gateway Service"""
    
    async def process_mpesa(self, phone: str, amount: float, reference: str) -> Dict[str, Any]:
        """Process M-Pesa payment"""
        return {
            "status": "pending",
            "message": "STK Push sent to " + phone,
            "reference": reference,
            "amount": amount
        }

# ============================================================
# 5. API ENDPOINTS
# ============================================================

security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    logger.info("🚀 Shambani Link Backend Starting...")
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("🛑 Shambani Link Backend Stopped")

app = FastAPI(
    title="Shambani Link API",
    description="Digital Agricultural Ecosystem Platform",
    version="4.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ HEALTH & STATUS ============
@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/v1")
async def api_info():
    """API Info"""
    return {"name": "Shambani Link API", "version": "1.0.0"}

# ============ AUTHENTICATION ============
@app.post("/api/v1/auth/register")
async def register(request: dict, db: Session = Depends(get_db)):
    """Register new user"""
    try:
        phone = request.get("phone_number")
        email = request.get("email")
        password = request.get("password")
        first_name = request.get("first_name")
        last_name = request.get("last_name")
        
        if not SecurityUtils.validate_phone_number(phone):
            raise HTTPException(status_code=400, detail="Invalid phone number")
        
        existing = db.query(User).filter(User.phone_number == phone).first()
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")
        
        new_user = User(
            id=str(uuid.uuid4()),
            phone_number=phone,
            email=email,
            password_hash=PasswordManager.hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role="farmer"
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        otp_code = OTPManager.generate_otp()
        otp = OTPRecord(
            id=str(uuid.uuid4()),
            user_id=new_user.id,
            phone_number=phone,
            otp_code=otp_code,
            otp_type="phone_verification",
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        db.add(otp)
        db.commit()
        
        logger.info(f"User registered: {phone}. OTP: {otp_code}")
        
        return {
            "status": "success",
            "message": "Registration successful. Verify phone.",
            "user_id": new_user.id,
            "phone_number": phone
        }
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/v1/auth/login")
async def login(request: dict, db: Session = Depends(get_db)):
    """Login user"""
    try:
        phone = request.get("phone_number")
        password = request.get("password")
        
        user = db.query(User).filter(User.phone_number == phone).first()
        if not user or not PasswordManager.verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not user.is_phone_verified:
            raise HTTPException(status_code=400, detail="Phone not verified")
        
        user.last_login = datetime.utcnow()
        db.commit()
        
        access_token = TokenManager.create_access_token(
            data={"sub": user.id, "phone": user.phone_number, "role": user.role}
        )
        
        return {
            "status": "success",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "phone_number": user.phone_number,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role
            }
        }
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/api/v1/auth/verify-otp")
async def verify_otp(request: dict, db: Session = Depends(get_db)):
    """Verify OTP"""
    try:
        phone = request.get("phone_number")
        otp_code = request.get("otp_code")
        
        otp = db.query(OTPRecord).filter(
            OTPRecord.phone_number == phone,
            OTPRecord.is_used == False
        ).order_by(OTPRecord.created_at.desc()).first()
        
        if not otp or datetime.utcnow() > otp.expires_at:
            raise HTTPException(status_code=400, detail="OTP expired")
        
        if otp.otp_code != otp_code:
            otp.attempts += 1
            db.commit()
            raise HTTPException(status_code=400, detail="Invalid OTP")
        
        otp.is_used = True
        otp.verified_at = datetime.utcnow()
        
        user = db.query(User).filter(User.phone_number == phone).first()
        if user:
            user.is_phone_verified = True
        
        db.commit()
        
        return {"status": "success", "message": "OTP verified"}
    except Exception as e:
        logger.error(f"OTP verification error: {e}")
        raise HTTPException(status_code=500, detail="Verification failed")

@app.post("/api/v1/auth/request-otp")
async def request_otp(request: dict, db: Session = Depends(get_db)):
    """Request OTP"""
    try:
        phone = request.get("phone_number")
        
        user = db.query(User).filter(User.phone_number == phone).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        otp_code = OTPManager.generate_otp()
        otp = OTPRecord(
            id=str(uuid.uuid4()),
            user_id=user.id,
            phone_number=phone,
            otp_code=otp_code,
            otp_type="phone_verification",
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        db.add(otp)
        db.commit()
        
        logger.info(f"OTP requested for {phone}. OTP: {otp_code}")
        
        return {"status": "success", "message": "OTP sent", "expires_in": 600}
    except Exception as e:
        logger.error(f"Request OTP error: {e}")
        raise HTTPException(status_code=500, detail="Request failed")

# ============ MARKETPLACE ============
@app.post("/api/v1/marketplace/crops")
async def create_crop(request: dict, credentials: HTTPAuthCredentials = Depends(security), db: Session = Depends(get_db)):
    """Create crop listing"""
    try:
        payload = TokenManager.verify_token(credentials.credentials)
        if not payload:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        user_id = payload.get("sub")
        
        crop = Crop(
            id=str(uuid.uuid4()),
            user_id=user_id,
            crop_name=request.get("crop_name"),
            crop_type=request.get("crop_type"),
            description=request.get("description"),
            quantity_kg=request.get("quantity_kg"),
            available_quantity_kg=request.get("quantity_kg"),
            price_per_kg=request.get("price_per_kg"),
            region=request.get("region"),
            district=request.get("district")
        )
        
        db.add(crop)
        db.commit()
        db.refresh(crop)
        
        return {
            "status": "success",
            "message": "Crop listed successfully",
            "crop_id": crop.id,
            "crop": {
                "id": crop.id,
                "crop_name": crop.crop_name,
                "quantity_kg": crop.quantity_kg,
                "price_per_kg": crop.price_per_kg
            }
        }
    except Exception as e:
        logger.error(f"Create crop error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create crop")

@app.get("/api/v1/marketplace/crops")
async def get_crops(region: Optional[str] = None, db: Session = Depends(get_db)):
    """Get crops listing"""
    try:
        query = db.query(Crop).filter(Crop.status == "available")
        if region:
            query = query.filter(Crop.region == region)
        
        crops = query.all()
        
        return {
            "status": "success",
            "count": len(crops),
            "crops": [
                {
                    "id": c.id,
                    "crop_name": c.crop_name,
                    "quantity_kg": c.quantity_kg,
                    "price_per_kg": c.price_per_kg,
                    "region": c.region,
                    "status": c.status
                }
                for c in crops
            ]
        }
    except Exception as e:
        logger.error(f"Get crops error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch crops")

# ============ LOANS ============
@app.post("/api/v1/loans/apply")
async def apply_loan(request: dict, credentials: HTTPAuthCredentials = Depends(security), db: Session = Depends(get_db)):
    """Apply for loan"""
    try:
        payload = TokenManager.verify_token(credentials.credentials)
        if not payload:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        user_id = payload.get("sub")
        
        # Calculate credit score
        scorer = CreditScorer()
        credit_result = await scorer.calculate_credit_score(user_id, db)
        
        if credit_result.get("status") == "error":
            raise HTTPException(status_code=400, detail="Unable to calculate credit score")
        
        loan_amount = float(request.get("loan_amount", 0))
        max_loan = credit_result.get("max_loan_amount", 0)
        
        if loan_amount > max_loan:
            return {
                "status": "rejected",
                "reason": f"Loan amount exceeds maximum of {max_loan}",
                "credit_score": credit_result.get("credit_score"),
                "max_loan": max_loan
            }
        
        loan = LoanApplication(
            id=str(uuid.uuid4()),
            user_id=user_id,
            loan_type=request.get("loan_type", "crop_loan"),
            loan_amount=loan_amount,
            interest_rate=credit_result.get("interest_rate", 12.0),
            loan_duration_months=request.get("duration_months", 12),
            purpose=request.get("purpose"),
            credit_score=credit_result.get("credit_score"),
            status="pending"
        )
        
        db.add(loan)
        db.commit()
        db.refresh(loan)
        
        return {
            "status": "success",
            "message": "Loan application submitted",
            "loan_id": loan.id,
            "credit_score": credit_result.get("credit_score"),
            "loan_amount": float(loan.loan_amount),
            "interest_rate": loan.interest_rate
        }
    except Exception as e:
        logger.error(f"Loan application error: {e}")
        raise HTTPException(status_code=500, detail="Loan application failed")

# ============ AI SERVICES ============
@app.post("/api/v1/ai/crop-doctor")
async def crop_doctor(request: dict):
    """AI Crop Doctor"""
    try:
        symptoms = request.get("symptoms", [])
        
        diagnostics = AIHealthDiagnostics()
        result = await diagnostics.diagnose_crop(symptoms)
        
        return result
    except Exception as e:
        logger.error(f"Crop doctor error: {e}")
        raise HTTPException(status_code=500, detail="Diagnosis failed")

@app.post("/api/v1/ai/livestock-doctor")
async def livestock_doctor(request: dict):
    """AI Livestock Doctor"""
    try:
        symptoms = request.get("symptoms", [])
        
        diagnostics = AIHealthDiagnostics()
        result = await diagnostics.diagnose_livestock(symptoms)
        
        return result
    except Exception as e:
        logger.error(f"Livestock doctor error: {e}")
        raise HTTPException(status_code=500, detail="Diagnosis failed")

@app.get("/api/v1/ai/credit-score")
async def get_credit_score(credentials: HTTPAuthCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get credit score"""
    try:
        payload = TokenManager.verify_token(credentials.credentials)
        if not payload:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        user_id = payload.get("sub")
        
        scorer = CreditScorer()
        result = await scorer.calculate_credit_score(user_id, db)
        
        return result
    except Exception as e:
        logger.error(f"Credit score error: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate score")

# ============ USSD ============
@app.post("/api/v1/ussd/callback")
async def ussd_callback(request: dict):
    """USSD callback handler"""
    try:
        phone = request.get("phoneNumber")
        text = request.get("text", "")
        session_id = request.get("sessionId")
        
        ussd = USSDService()
        response = await ussd.handle_ussd(phone, text)
        
        return {
            "USERID": session_id,
            "action": "prompt" if response.startswith("CON") else "end",
            "menus": response
        }
    except Exception as e:
        logger.error(f"USSD error: {e}")
        return {"action": "end", "menus": "Kosa! Jaribu tena."}

# ============ PAYMENTS ============
@app.post("/api/v1/payments/mpesa")
async def initiate_mpesa(request: dict, credentials: HTTPAuthCredentials = Depends(security)):
    """Initiate M-Pesa payment"""
    try:
        payload = TokenManager.verify_token(credentials.credentials)
        if not payload:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        phone = request.get("phone_number")
        amount = request.get("amount")
        reference = request.get("reference", str(uuid.uuid4()))
        
        gateway = PaymentGateway()
        result = await gateway.process_mpesa(phone, amount, reference)
        
        return result
    except Exception as e:
        logger.error(f"M-Pesa error: {e}")
        raise HTTPException(status_code=500, detail="Payment failed")

# ============ ERROR HANDLERS ============
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "status": "error",
        "detail": exc.detail,
        "status_code": exc.status_code
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "__main__:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
