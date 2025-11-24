# app/services/user_service.py
import logging
from datetime import datetime, date
from app.models.user import User

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db):
        self.db = db
    
    async def get_or_create_user(self, user_id: int) -> User:
        """Получить пользователя или создать нового"""
        user = await self.db.get_user(user_id)
        if not user:
            user = User(
                user_id=user_id,
                created_at=datetime.now(),
                last_reset_date=date.today()
            )
            await self.db.save_user(user)
            logger.info(f"Создан новый пользователь: {user_id}")
        return user
    
    async def increment_photo_counter(self, user_id: int) -> bool:
        """Увеличить счетчик фото и проверить лимит"""
        user = await self.get_or_create_user(user_id)
        
        # Проверяем нужно ли сбросить счетчики
        await self._reset_daily_counters_if_needed(user)
        
        if not user.has_photo_quota():
            return False
            
        user.daily_photos_used += 1
        await self.db.save_user(user)
        return True
    
    async def increment_text_counter(self, user_id: int) -> bool:
        """Увеличить счетчик текстов"""
        user = await self.get_or_create_user(user_id)
        await self._reset_daily_counters_if_needed(user)
        
        if not user.has_text_quota():
            return False
            
        user.daily_texts_used += 1
        await self.db.save_user(user)
        return True
    
    async def _reset_daily_counters_if_needed(self, user: User):
        """Сбросить дневные счетчики если наступил новый день"""
        if user.last_reset_date != date.today():
            user.daily_photos_used = 0
            user.daily_texts_used = 0
            user.last_reset_date = date.today()
            await self.db.save_user(user)
    
    async def get_user_limits_info(self, user_id: int) -> Dict:
        """Получить информацию о лимитах пользователя"""
        user = await self.get_or_create_user(user_id)
        return {
            "photos_used": user.daily_photos_used,
            "photos_limit": user.get_photo_limit(),
            "texts_used": user.daily_texts_used,
            "texts_limit": user.get_text_limit(),
            "is_premium": user.is_premium(),
            "subscription_type": user.subscription_type,
            "subscription_until": user.subscription_until
        }