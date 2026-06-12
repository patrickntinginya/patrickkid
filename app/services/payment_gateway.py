"""
Payment Gateway Integration
M-Pesa, Stripe, and other payment methods
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import uuid

logger = logging.getLogger(__name__)

class MPesaGateway:
    """M-Pesa Payment Gateway Integration"""
    
    def __init__(self, consumer_key: str, consumer_secret: str, shortcode: str, passkey: str):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.shortcode = shortcode
        self.passkey = passkey
        self.base_url = "https://api.safaricom.co.ke"
    
    async def initiate_payment(self, phone: str, amount: float, reference: str) -> Dict[str, Any]:
        """
        Initiate M-Pesa STK Push payment
        """
        try:
            # Generate access token
            import requests
            import base64
            from datetime import datetime
            
            auth = base64.b64encode(
                f"{self.consumer_key}:{self.consumer_secret}".encode()
            ).decode()
            
            headers = {"Authorization": f"Basic {auth}"}
            
            # Get access token
            token_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
            token_response = requests.get(token_url, headers=headers)
            access_token = token_response.json().get("access_token")
            
            # Prepare STK Push
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            password = base64.b64encode(
                f"{self.shortcode}{self.passkey}{timestamp}".encode()
            ).decode()
            
            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),
                "PartyA": phone,
                "PartyB": self.shortcode,
                "PhoneNumber": phone,
                "CallBackURL": "https://api.shambani-link.com/api/v1/payments/mpesa-callback",
                "AccountReference": reference,
                "TransactionDesc": "Shambani Link Payment"
            }
            
            headers["Authorization"] = f"Bearer {access_token}"
            headers["Content-Type"] = "application/json"
            
            stk_url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            response = requests.post(stk_url, json=payload, headers=headers)
            
            result = response.json()
            
            if result.get("ResponseCode") == "0":
                return {
                    "status": "success",
                    "checkout_request_id": result.get("CheckoutRequestID"),
                    "message": "STK Push sent successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": result.get("ResponseDescription")
                }
        
        except Exception as e:
            logger.error(f"M-Pesa payment error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def verify_payment(self, checkout_request_id: str) -> Dict[str, Any]:
        """
        Verify M-Pesa payment status
        """
        try:
            # Query payment status
            import requests
            import base64
            from datetime import datetime
            
            auth = base64.b64encode(
                f"{self.consumer_key}:{self.consumer_secret}".encode()
            ).decode()
            
            headers = {"Authorization": f"Basic {auth}"}
            token_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
            token_response = requests.get(token_url, headers=headers)
            access_token = token_response.json().get("access_token")
            
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            password = base64.b64encode(
                f"{self.shortcode}{self.passkey}{timestamp}".encode()
            ).decode()
            
            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }
            
            headers["Authorization"] = f"Bearer {access_token}"
            headers["Content-Type"] = "application/json"
            
            query_url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
            response = requests.post(query_url, json=payload, headers=headers)
            
            result = response.json()
            
            return {
                "status": "success" if result.get("ResponseCode") == "0" else "pending",
                "response_code": result.get("ResponseCode"),
                "result_code": result.get("ResultCode")
            }
        
        except Exception as e:
            logger.error(f"M-Pesa verification error: {e}")
            return {"status": "error", "message": str(e)}

class StripeGateway:
    """Stripe Payment Gateway Integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            import stripe
            stripe.api_key = api_key
            self.stripe = stripe
        except ImportError:
            logger.warning("Stripe library not installed")
    
    async def create_payment_intent(self, amount: float, currency: str, description: str) -> Dict[str, Any]:
        """
        Create Stripe payment intent
        """
        try:
            intent = self.stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency.lower(),
                description=description
            )
            
            return {
                "status": "success",
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id
            }
        
        except Exception as e:
            logger.error(f"Stripe error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Confirm Stripe payment
        """
        try:
            intent = self.stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                "status": "success" if intent.status == "succeeded" else intent.status,
                "payment_intent_id": intent.id,
                "amount": intent.amount / 100,
                "currency": intent.currency
            }
        
        except Exception as e:
            logger.error(f"Stripe confirmation error: {e}")
            return {"status": "error", "message": str(e)}

class PaymentProcessor:
    """Main Payment Processor"""
    
    def __init__(self, mpesa_gateway: MPesaGateway = None, stripe_gateway: StripeGateway = None):
        self.mpesa = mpesa_gateway
        self.stripe = stripe_gateway
    
    async def process_payment(self, payment_method: str, **kwargs) -> Dict[str, Any]:
        """
        Process payment based on method
        """
        if payment_method == "mpesa":
            return await self.mpesa.initiate_payment(
                phone=kwargs.get("phone"),
                amount=kwargs.get("amount"),
                reference=kwargs.get("reference")
            )
        
        elif payment_method == "stripe":
            return await self.stripe.create_payment_intent(
                amount=kwargs.get("amount"),
                currency=kwargs.get("currency", "USD"),
                description=kwargs.get("description")
            )
        
        else:
            return {"status": "error", "message": "Unsupported payment method"}