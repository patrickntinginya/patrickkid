"""
USSD Service
Handles USSD menu and SMS interactions
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class USSDMenu:
    """USSD Menu Structure"""
    
    MAIN_MENU = """
**** Karibu Shambani Link ****
1. Bei za Soko
2. Uza Mazao
3. Uza Mifugo
4. Omba Mkopo
5. Omba Usafiri
6. Bima
7. Malipo
8. Historia ya Mauzo
9. AI Ushauri
0. Wasiliana na Mnunuzi
"""
    
    MARKET_PRICES = """
**** Bei za Soko ****
1. Mahindi
2. Wali
3. Maharagwe
4. Ngano
5. Nyanya
0. Rudi Nyuma
"""
    
    SELL_CROPS = """
**** Uza Mazao ****
Ingiza jina la mazao:
"""
    
    SELL_LIVESTOCK = """
**** Uza Mifugo ****
1. Ng'ombe
2. Mbuzi
3. Kuku
4. Kuchinja
0. Rudi Nyuma
"""
    
    LOAN_TYPES = """
**** Omba Mkopo ****
1. Mkopo wa Mazao
2. Mkopo wa Mifugo
3. Mkopo wa Vifaa
0. Rudi Nyuma
"""
    
    INSURANCE = """
**** Bima ****
1. Bima ya Mazao
2. Bima ya Mifugo
0. Rudi Nyuma
"""

class USSDService:
    """USSD Service Handler"""
    
    def __init__(self, db):
        self.db = db
    
    async def handle_ussd(self, phone: str, text: str, session_id: str) -> str:
        """
        Handle USSD request
        
        Args:
            phone: User phone number
            text: USSD input text
            session_id: USSD session ID
        
        Returns:
            USSD menu response
        """
        try:
            # Parse input
            menu_stack = text.split("*") if text else []
            
            if len(menu_stack) == 0:
                return "CON " + USSDMenu.MAIN_MENU
            
            choice = menu_stack[-1]
            
            # Handle main menu
            if len(menu_stack) == 1:
                return await self._handle_main_menu(choice, phone)
            
            # Handle sub menus
            elif len(menu_stack) == 2:
                main_choice = menu_stack[0]
                sub_choice = menu_stack[1]
                return await self._handle_submenu(main_choice, sub_choice, phone)
            
            else:
                return await self._handle_deep_menu(menu_stack, phone)
        
        except Exception as e:
            logger.error(f"USSD error: {e}")
            return "END Kosa! Tafadhali jaribu tena."
    
    async def _handle_main_menu(self, choice: str, phone: str) -> str:
        """
        Handle main menu selection
        """
        if choice == "1":
            return "CON " + USSDMenu.MARKET_PRICES
        elif choice == "2":
            return "CON " + USSDMenu.SELL_CROPS
        elif choice == "3":
            return "CON " + USSDMenu.SELL_LIVESTOCK
        elif choice == "4":
            return "CON " + USSDMenu.LOAN_TYPES
        elif choice == "5":
            return "CON Ingiza mahali pa kutofautiana:\n"
        elif choice == "6":
            return "CON " + USSDMenu.INSURANCE
        elif choice == "7":
            return "CON Ingiza kiasi cha malipo:\n"
        elif choice == "8":
            return await self._get_sales_history(phone)
        elif choice == "9":
            return "CON Karibu Shambani AI. Ingiza swali:\n"
        elif choice == "0":
            return "END Asante kwa kutumia Shambani Link!"
        else:
            return "CON " + USSDMenu.MAIN_MENU
    
    async def _handle_submenu(self, main_choice: str, sub_choice: str, phone: str) -> str:
        """
        Handle sub-menu selection
        """
        if main_choice == "1":  # Market Prices
            return await self._get_market_price(sub_choice)
        elif main_choice == "2":  # Sell Crops
            return "CON Ingiza bei ya kila kilo:\n"
        elif main_choice == "3":  # Sell Livestock
            return "CON Ingiza idadi ya wanyama:\n"
        elif main_choice == "4":  # Loan
            return "CON Ingiza kiasi cha mkopo (TZS):\n"
        elif main_choice == "6":  # Insurance
            return "CON Ingiza thamani ya kitu cha kupanga bima:\n"
        else:
            return "END Chaguo si sahihi"
    
    async def _handle_deep_menu(self, menu_stack: list, phone: str) -> str:
        """
        Handle deep menu selections
        """
        # Process form submissions
        return "END Asante! Ombi lako limepokewa. Utapokea ujumbe wa kuthibitisha."
    
    async def _get_market_price(self, crop_code: str) -> str:
        """
        Get market price for crop
        """
        prices = {
            "1": "Mahindi: TZS 820/kg\nHabari: Imepanda 2% leo",
            "2": "Wali: TZS 1200/kg\nHabari: Imeshuka 1% leo",
            "3": "Maharagwe: TZS 950/kg\nHabari: Imepanda 3% leo",
            "4": "Ngano: TZS 880/kg\nHabari: Imepanda 1% leo",
            "5": "Nyanya: TZS 650/kg\nHabari: Imeshuka 2% leo"
        }
        
        price = prices.get(crop_code, "Bidhaa haijulikani")
        return f"END {price}\n\nMtu anayenunua karibu:\nMchumi - Dar es Salaam"
    
    async def _get_sales_history(self, phone: str) -> str:
        """
        Get user sales history
        """
        try:
            from app.models.user import User
            from app.models.marketplace import Order
            
            user = self.db.query(User).filter(User.phone_number == phone).first()
            if not user:
                return "END Watumiaji haijulikani"
            
            orders = self.db.query(Order).filter(
                Order.seller_id == user.id,
                Order.status == "delivered"
            ).all()
            
            if not orders:
                return "END Hamuna historia ya mauzo"
            
            history = "Historia ya Mauzo:\n"
            for order in orders[-5:]:  # Last 5 sales
                history += f"- {order.quantity} units @ {order.unit_price}\n"
            
            return f"END {history}"
        
        except Exception as e:
            logger.error(f"Sales history error: {e}")
            return "END Kosa! Tafadhali jaribu tena."

class SMSNotifier:
    """SMS Notification Service"""
    
    def __init__(self, api_key: str, api_username: str):
        self.api_key = api_key
        self.api_username = api_username
    
    async def send_sms(self, phone: str, message: str) -> bool:
        """
        Send SMS notification
        """
        try:
            import africastalking
            
            africastalking.initialize(
                username=self.api_username,
                api_key=self.api_key
            )
            
            sms = africastalking.SMS
            response = sms.send(message, [phone])
            
            if response["SMSMessageData"]["Recipients"][0]["statusCode"] == 101:
                return True
            return False
        
        except Exception as e:
            logger.error(f"SMS send error: {e}")
            return False
    
    async def send_bulk_sms(self, phones: list, message: str) -> bool:
        """
        Send bulk SMS
        """
        try:
            import africastalking
            
            africastalking.initialize(
                username=self.api_username,
                api_key=self.api_key
            )
            
            sms = africastalking.SMS
            response = sms.send(message, phones)
            
            return len(response["SMSMessageData"]["Recipients"]) > 0
        
        except Exception as e:
            logger.error(f"Bulk SMS error: {e}")
            return False
