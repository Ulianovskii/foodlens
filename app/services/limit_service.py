from datetime import datetime
from app.models.user import User

class LimitService:
    def __init__(self, database):  # ← ИСПРАВИТЬ ТИП
        self.database = database
    
    async def check_and_increment_usage(self, user: User) -> bool:
        """Проверить лимит и увеличить счетчик"""
        # Проверяем нужно ли сбросить дневной счетчик
        await self._reset_daily_if_needed(user)
        
        if not user.can_analyze_photo():
            return False
        
        user.daily_photos_used += 1
        user.total_photos_analyzed += 1
        await self.database.save_user(user.to_dict())
        return True
    
    async def _reset_daily_if_needed(self, user: User):
        """Сбросить дневной счетчик если наступил новый день"""
        today = datetime.now().date()
        last_reset_date = user.last_reset_date
        
        if today > last_reset_date:
            user.reset_daily_counter()
            await self.database.save_user(user.to_dict())
    
    async def reset_user_limits(self, telegram_id: int) -> bool:
        """Сбросить лимиты пользователя по telegram_id"""
        user_data = await self.database.get_user(telegram_id)
        if not user_data:
            return False
        
        user = User.from_dict(user_data)
        user.reset_daily_counter()
        await self.database.save_user(user.to_dict())
        return True
    
    async def reset_my_limits(self, user: User):
        """Сбросить лимиты текущего пользователя"""
        user.reset_daily_counter()
        await self.database.save_user(user.to_dict())