from app.models.user import User
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, database):
        self.database = database
    
    async def get_or_create_user(self, telegram_id: int, username: str = None, 
                               first_name: str = None, last_name: str = None) -> User:
        """Получить пользователя или создать нового"""
        user_data = await self.database.get_user(telegram_id)
        
        if user_data:
            # Конвертируем dict в User объект
            user = User.from_dict(user_data)
            # Обновляем данные если нужно
            if username and user.username != username:
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                await self.save_user(user)
            return user
        else:
            # Создаем нового пользователя
            user = User(
                user_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                created_at=datetime.now(),
                last_reset_date=date.today()
            )
            await self.save_user(user)
            return user
    
    async def save_user(self, user: User):
        """Сохраняет User объект в БД"""
        try:
            user_data = user.to_dict()
            await self.database.save_user(user_data)
        except Exception as e:
            logger.error(f"Ошибка в save_user: {e}")
            raise
    
    async def increment_photo_counter(self, user: User) -> bool:
        """Увеличить счетчик фото и проверить лимит"""
        # Проверяем нужно ли сбросить счетчики
        await self._reset_daily_counters_if_needed(user)
        
        if not user.can_analyze_photo():
            return False
            
        user.daily_photos_used += 1
        user.total_photos_analyzed += 1
        await self.save_user(user)
        return True
    
    async def _reset_daily_counters_if_needed(self, user: User):
        """Сбросить дневные счетчики если наступил новый день"""
        if user.last_reset_date != date.today():
            user.daily_photos_used = 0
            user.last_reset_date = date.today()
            await self.save_user(user)
    
    async def get_user(self, user_id: int) -> User:
        """Получить пользователя по ID"""
        user_data = await self.database.get_user(user_id)
        if user_data:
            return User.from_dict(user_data)
        return None

    async def update_subscription(self, user_id: int, subscription_type: str, subscription_until: datetime = None):
        """Обновляет подписку пользователя"""
        user = await self.get_user(user_id)
        if user:
            user.subscription_type = subscription_type
            user.subscription_until = subscription_until
            await self.save_user(user)

    async def reset_daily_limits(self, user_id: int):
        """Сбрасывает дневные лимиты пользователя"""
        user = await self.get_user(user_id)
        if user:
            user.daily_photos_used = 0
            user.last_reset_date = date.today()
            await self.save_user(user)