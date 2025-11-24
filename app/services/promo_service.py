import secrets
import string
from datetime import datetime, timedelta
from typing import List, Optional
from app.models.promo import PromoCode, PromoType
from app.models.user import User

class PromoService:
    def __init__(self, database):
        self.database = database
    
    def generate_promo_code(self, length=8) -> str:
        """Сгенерировать уникальный промокод"""
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    async def create_promo_codes(self, promo_type: str, count: int = 1, days_valid: int = 30) -> List[str]:
        """Создать несколько промокодов"""
        promo_codes = []
        
        for _ in range(count):
            code = self.generate_promo_code()
            expires_at = datetime.now() + timedelta(days=days_valid)
            
            # Сохраняем в БД
            await self.database.save_promo_code({
                'code': code,
                'promo_type': promo_type,
                'expires_at': expires_at
            })
            promo_codes.append(code)
        
        return promo_codes
    
    async def activate_promo_code(self, code: str, user: User) -> bool:
        """Активировать промокод для пользователя"""
        # Получаем промокод из БД
        promo_data = await self.database.get_promo_code(code)
        if not promo_data:
            return False
        
        promo = PromoCode.from_dict(promo_data)
        
        if not promo.is_valid():
            return False
        
        # Активируем подписку
        subscription_days = promo.get_subscription_days()
        user.subscription_type = promo.promo_type
        user.subscription_until = datetime.now() + timedelta(days=subscription_days)
        
        # Отмечаем промокод как использованный
        await self.database.mark_promo_code_used(code, user.user_id)
        
        # Сохраняем пользователя
        await self.database.save_user(user.to_dict())
        
        return True
    
    async def get_all_promo_codes(self) -> List[PromoCode]:
        """Получить все промокоды"""
        promo_data_list = await self.database.get_all_promo_codes()
        return [PromoCode.from_dict(data) for data in promo_data_list]
    
    async def reset_promo_codes(self):
        """Сбросить все промокоды (для тестирования)"""
        await self.database.reset_promo_codes()