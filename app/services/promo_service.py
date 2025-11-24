# app/services/promo_service.py
import secrets
import string
from datetime import datetime, timedelta
from typing import List, Tuple
import logging

from app.models.promo import PromoCode
from app.models.user import User
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

class PromoService:
    def __init__(self, database):
        self.database = database
        self.user_service = UserService(database)
    
    def generate_promo_code(self, length=8) -> str:
        """Сгенерировать уникальный промокод"""
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    async def create_promo_codes(self, promo_type: str, count: int = 1, days_valid: int = 30) -> List[str]:
        """Создать несколько промокодов"""
        promo_codes = []
        
        for _ in range(count):
            # Генерируем уникальный код
            while True:
                code = self.generate_promo_code()
                existing_promo = await self.database.get_promo_code(code)
                if not existing_promo:
                    break
            
            expires_at = datetime.now() + timedelta(days=days_valid)
            
            # Сохраняем в БД
            await self.database.save_promo_code({
                'code': code,
                'promo_type': promo_type,
                'expires_at': expires_at,
                'is_used': False,
                'used_by': None,
                'used_at': None,
                'created_at': datetime.now()
            })
            promo_codes.append(code)
        
        return promo_codes
    
    async def activate_promo_code(self, code: str, user: User) -> Tuple[bool, str]:
        """Активировать промокод для пользователя"""
        try:
            # Получаем промокод из БД
            promo_data = await self.database.get_promo_code(code)
            if not promo_data:
                return False, "Промокод не найден"
            
            promo = PromoCode.from_dict(promo_data)
            
            # Проверяем валидность промокода
            if promo.is_used:
                return False, "Промокод уже использован"
            
            if promo.expires_at and promo.expires_at < datetime.now():
                return False, "Промокод просрочен"
            
            # Проверяем, нет ли у пользователя активной подписки
            if user.subscription_type != "free" and user.subscription_until and user.subscription_until > datetime.now():
                return False, "У вас уже есть активная подписка"
            
            # Определяем тип подписки и срок
            if "week" in promo.promo_type:
                days = 7
                sub_type = "premium_week"
            elif "month" in promo.promo_type:
                days = 30
                sub_type = "premium_month"
            else:
                days = 7  # по умолчанию неделя
                sub_type = "premium_week"
            
            # Активируем подписку пользователю
            subscription_until = datetime.now() + timedelta(days=days)
            await self.user_service.update_subscription(
                user.user_id, 
                sub_type, 
                subscription_until
            )
            
            # Отмечаем промокод как использованный
            await self.database.mark_promo_code_used(code, user.user_id, datetime.now())
            
            logger.info(f"✅ Промокод {code} активирован для пользователя {user.user_id}")
            return True, "Успешно"
            
        except Exception as e:
            logger.error(f"❌ Ошибка активации промокода {code}: {e}")
            return False, f"Ошибка: {e}"
    
    async def get_promo_by_code(self, code: str) -> PromoCode:
        """Получить промокод по коду"""
        promo_data = await self.database.get_promo_code(code)
        if promo_data:
            return PromoCode.from_dict(promo_data)
        return None
    
    async def get_all_promo_codes(self) -> List[PromoCode]:
        """Получить все промокоды"""
        promo_data_list = await self.database.get_all_promo_codes()
        return [PromoCode.from_dict(data) for data in promo_data_list]
    
    async def reset_promo_codes(self):
        """Сбросить все промокоды (для тестирования)"""
        await self.database.reset_promo_codes()