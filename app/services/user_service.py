# app/services/user_service.py - ИСПРАВЛЕННЫЙ
from app.models.user import User
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, database):
        self.database = database
    
    async def get_or_create_user(self, user_id: int) -> User:
        """Получить пользователя или создать нового"""
        user_data = await self.database.get_user(user_id)
        
        if user_data:
            # Конвертируем dict в User объект
            return User.from_dict(user_data)
        else:
            # Создаем нового пользователя
            user = User(
                user_id=user_id,
                created_at=datetime.now(),
                last_reset_date=date.today()
            )
            await self.save_user(user)
            return user
    
    async def save_user(self, user: User):
        """Сохраняет User объект в БД"""
        try:
            user_data = user.to_dict()
            print(f"DEBUG: user_data type: {type(user_data)}")  # ← ДОБАВИТЬ
            print(f"DEBUG: user_data keys: {user_data.keys() if isinstance(user_data, dict) else 'NOT DICT'}")  # ← ДОБАВИТЬ
            await self.database.save_user(user_data)
        except Exception as e:
            logger.error(f"Ошибка в save_user: {e}")
            raise
    
    async def increment_photo_counter(self, user_id: int) -> bool:
        """Увеличить счетчик фото и проверить лимит"""
        user = await self.get_or_create_user(user_id)
        
        # Проверяем нужно ли сбросить счетчики
        await self._reset_daily_counters_if_needed(user)
        
        if not user.has_photo_quota():
            return False
            
        user.daily_photos_used += 1
        await self.save_user(user)
        return True
    
    async def _reset_daily_counters_if_needed(self, user: User):
        """Сбросить дневные счетчики если наступил новый день"""
        if user.last_reset_date != date.today():
            user.daily_photos_used = 0
            user.daily_texts_used = 0
            user.last_reset_date = date.today()
            await self.save_user(user)