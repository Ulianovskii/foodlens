# app/models/user.py - ИСПРАВЛЕННЫЙ (убрать дубли)
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional

@dataclass
class User:
    user_id: int
    created_at: datetime
    language: str = "ru"
    subscription_type: str = "free"
    subscription_until: Optional[datetime] = None
    daily_photos_used: int = 0
    daily_texts_used: int = 0
    last_reset_date: Optional[date] = None
    custom_photo_limit: Optional[int] = None
    custom_text_limit: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Создает User из данных БД, игнорируя лишние поля"""
        # Создаем копию без лишних полей
        filtered_data = {k: v for k, v in data.items() 
                        if k in cls.__dataclass_fields__}
        return cls(**filtered_data)
    
    def to_dict(self) -> dict:
        """Конвертирует User в dict для БД"""
        return {
            'user_id': self.user_id,
            'created_at': self.created_at,
            'language': self.language,
            'subscription_type': self.subscription_type,
            'subscription_until': self.subscription_until,
            'daily_photos_used': self.daily_photos_used,
            'daily_texts_used': self.daily_texts_used,
            'last_reset_date': self.last_reset_date,
            'custom_photo_limit': self.custom_photo_limit,
            'custom_text_limit': self.custom_text_limit
        }
    
    def has_photo_quota(self) -> bool:
        """Проверяет, есть ли у пользователя доступные фото-запросы"""
        daily_limit = self._get_daily_photo_limit()
        return self.daily_photos_used < daily_limit
    
    def _get_daily_photo_limit(self) -> int:
        """Возвращает дневной лимит фото в зависимости от подписки"""
        if self.custom_photo_limit:
            return self.custom_photo_limit
        
        limits = {
            'free': 3,
            'premium_week': 10,
            'premium_month': 10
        }
        return limits.get(self.subscription_type, 3)