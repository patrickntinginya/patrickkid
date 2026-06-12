"""
AI Services
Crop Doctor, Livestock Doctor, Market Forecast, AI Scoring
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class AIHealthDiagnostics:
    """AI Health Diagnostics Service"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.diseases = self._load_disease_db()
    
    def _load_disease_db(self) -> Dict[str, Dict[str, Any]]:
        """
        Load disease knowledge base
        """
        return {
            "crops": {
                "early_blight": {
                    "name": "Early Blight",
                    "symptoms": ["brown spots", "yellowing leaves", "stem lesions"],
                    "treatment": ["fungicide application", "remove infected leaves", "improve drainage"],
                    "prevention": ["crop rotation", "resistant varieties", "proper spacing"]
                },
                "powdery_mildew": {
                    "name": "Powdery Mildew",
                    "symptoms": ["white powder on leaves", "curled leaves", "stunted growth"],
                    "treatment": ["sulfur spray", "neem oil", "remove affected parts"],
                    "prevention": ["good air circulation", "avoid overhead watering"]
                },
                "leaf_spot": {
                    "name": "Leaf Spot Disease",
                    "symptoms": ["circular spots", "yellow halo", "premature leaf drop"],
                    "treatment": ["copper fungicide", "remove infected leaves"],
                    "prevention": ["sanitation", "avoid wetting leaves", "crop rotation"]
                }
            },
            "livestock": {
                "foot_and_mouth": {
                    "name": "Foot and Mouth Disease",
                    "symptoms": ["blisters on hooves", "drooling", "lameness", "fever"],
                    "treatment": ["quarantine", "supportive care", "contact veterinarian"],
                    "prevention": ["vaccination", "biosecurity", "hygiene"]
                },
                "mastitis": {
                    "name": "Mastitis",
                    "symptoms": ["swollen udder", "abnormal milk", "fever", "reduced milk yield"],
                    "treatment": ["antibiotics", "milking hygiene", "milk out frequently"],
                    "prevention": ["clean milking", "teat dipping", "proper nutrition"]
                },
                "pneumonia": {
                    "name": "Respiratory Disease",
                    "symptoms": ["coughing", "nasal discharge", "lethargy", "fever"],
                    "treatment": ["antibiotics", "rest", "good ventilation"],
                    "prevention": ["proper ventilation", "vaccination", "stress reduction"]
                }
            }
        }
    
    async def diagnose_crop(self, symptoms: List[str], images: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Diagnose crop disease
        """
        try:
            # Simple keyword matching (would use ML model in production)
            matching_diseases = []
            
            for disease_key, disease_info in self.diseases["crops"].items():
                matching_symptoms = [s for s in symptoms if any(keyword in s.lower() for keyword in disease_info["symptoms"])]
                
                if matching_symptoms:
                    matching_diseases.append({
                        "disease": disease_info["name"],
                        "confidence": len(matching_symptoms) / len(disease_info["symptoms"]),
                        "symptoms_matched": matching_symptoms,
                        "treatment": disease_info["treatment"],
                        "prevention": disease_info["prevention"]
                    })
            
            # Sort by confidence
            matching_diseases.sort(key=lambda x: x["confidence"], reverse=True)
            
            return {
                "status": "success",
                "diagnoses": matching_diseases[:3],  # Top 3 diagnoses
                "recommendation": "Tafadhali wasiliana na mganga wa wanyama au mwalimu wa kilimo kwa msaada zaidi."
            }
        
        except Exception as e:
            logger.error(f"Crop diagnosis error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def diagnose_livestock(self, symptoms: List[str]) -> Dict[str, Any]:
        """
        Diagnose livestock disease
        """
        try:
            matching_diseases = []
            
            for disease_key, disease_info in self.diseases["livestock"].items():
                matching_symptoms = [s for s in symptoms if any(keyword in s.lower() for keyword in disease_info["symptoms"])]
                
                if matching_symptoms:
                    matching_diseases.append({
                        "disease": disease_info["name"],
                        "confidence": len(matching_symptoms) / len(disease_info["symptoms"]),
                        "symptoms_matched": matching_symptoms,
                        "treatment": disease_info["treatment"],
                        "prevention": disease_info["prevention"]
                    })
            
            matching_diseases.sort(key=lambda x: x["confidence"], reverse=True)
            
            return {
                "status": "success",
                "diagnoses": matching_diseases[:3],
                "urgency": "HIGH" if matching_diseases and matching_diseases[0]["confidence"] > 0.8 else "NORMAL",
                "recommendation": "Mwaliko wa mifugo anatakiwa kutembelea haraka."
            }
        
        except Exception as e:
            logger.error(f"Livestock diagnosis error: {e}")
            return {"status": "error", "message": str(e)}

class MarketForecaster:
    """Market Price Forecasting Service"""
    
    def __init__(self, db):
        self.db = db
    
    async def forecast_price(self, product: str, region: str, days: int = 30) -> Dict[str, Any]:
        """
        Forecast market price
        """
        try:
            from app.models.marketplace import MarketPrice
            from sqlalchemy import desc
            
            # Get historical prices
            prices = self.db.query(MarketPrice).filter(
                MarketPrice.product_name == product,
                MarketPrice.region == region
            ).order_by(desc(MarketPrice.recorded_at)).limit(30).all()
            
            if not prices:
                return {
                    "status": "no_data",
                    "message": "Kutokuwako data ya soko kwa bidhaa hii"
                }
            
            # Simple trend analysis
            price_values = [float(p.price) for p in prices]
            avg_price = sum(price_values) / len(price_values)
            trend = "up" if price_values[0] > avg_price else "down"
            
            # Estimate forecast
            forecast_prices = []
            for i in range(1, days + 1):
                if trend == "up":
                    forecast = avg_price * (1 + (0.02 * (i / 30)))
                else:
                    forecast = avg_price * (1 - (0.02 * (i / 30)))
                forecast_prices.append({
                    "day": i,
                    "predicted_price": round(forecast, 2)
                })
            
            return {
                "status": "success",
                "product": product,
                "region": region,
                "current_price": price_values[0],
                "average_price": round(avg_price, 2),
                "trend": trend,
                "forecast": forecast_prices,
                "recommendation": f"Bei inaonekana kuwa {trend}. Karibu kununua sasa." if trend == "up" else f"Bei inaonekana kushuka. Subiri kidogo kabla ya kuuza."
            }
        
        except Exception as e:
            logger.error(f"Price forecasting error: {e}")
            return {"status": "error", "message": str(e)}

class CreditScorer:
    """AI Credit Scoring System"""
    
    def __init__(self, db):
        self.db = db
    
    async def calculate_credit_score(self, user_id: str) -> Dict[str, Any]:
        """
        Calculate credit score based on user data
        """
        try:
            from app.models.user import User
            from app.models.finance import LoanApplication, LoanRepayment
            from app.models.marketplace import Order
            
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"status": "error", "message": "User not found"}
            
            score = 300  # Base score
            factors = {}
            
            # User verification (max 150 points)
            if user.is_verified:
                factors["verification"] = 150
                score += 150
            elif user.is_phone_verified:
                factors["phone_verification"] = 75
                score += 75
            
            # User rating (max 150 points)
            if user.average_rating > 4.5:
                factors["rating"] = 150
                score += 150
            elif user.average_rating > 4.0:
                factors["rating"] = 100
                score += 100
            elif user.average_rating > 3.0:
                factors["rating"] = 50
                score += 50
            
            # Order history (max 200 points)
            orders = self.db.query(Order).filter(
                (Order.buyer_id == user_id) | (Order.seller_id == user_id),
                Order.status == "delivered"
            ).all()
            
            if len(orders) > 10:
                factors["order_history"] = 200
                score += 200
            elif len(orders) > 5:
                factors["order_history"] = 100
                score += 100
            elif len(orders) > 0:
                factors["order_history"] = 50
                score += 50
            
            # Loan history (max 200 points)
            loans = self.db.query(LoanApplication).filter(LoanApplication.user_id == user_id).all()
            repayments = self.db.query(LoanRepayment).filter(LoanRepayment.loan_id.in_([l.id for l in loans])).all()
            
            if loans:
                on_time_repayments = len([r for r in repayments if r.status == "completed"])
                repayment_rate = on_time_repayments / len(repayments) if repayments else 0
                
                if repayment_rate > 0.9:
                    factors["loan_history"] = 200
                    score += 200
                elif repayment_rate > 0.7:
                    factors["loan_history"] = 100
                    score += 100
                elif repayment_rate > 0.5:
                    factors["loan_history"] = 50
                    score += 50
            
            # Determine credit tier
            if score >= 900:
                tier = "EXCELLENT"
                max_loan = 10000000  # 10M TZS
                interest_rate = 8.0
            elif score >= 750:
                tier = "GOOD"
                max_loan = 5000000  # 5M TZS
                interest_rate = 12.0
            elif score >= 600:
                tier = "FAIR"
                max_loan = 2000000  # 2M TZS
                interest_rate = 15.0
            else:
                tier = "POOR"
                max_loan = 500000  # 500K TZS
                interest_rate = 18.0
            
            return {
                "status": "success",
                "user_id": user_id,
                "credit_score": score,
                "credit_tier": tier,
                "factors": factors,
                "max_loan_amount": max_loan,
                "interest_rate": interest_rate,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Credit scoring error: {e}")
            return {"status": "error", "message": str(e)}
