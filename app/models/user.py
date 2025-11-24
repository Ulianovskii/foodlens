from datetime import datetime, date
from enum import Enum
from typing import Optional

class SubscriptionType(Enum):
    FREE = "free"
    PREMIUM_WEEK = "premium_week" 
    PREMIUM_MONTH = "premium_month"

class User:
    def __init__(
        self,
        user_id: int,
        created_at: datetime = None,
        language: str = "ru",
        subscription_type: str = "free",
        subscription_until: datetime = None,
        daily_photos_used: int = 0,
        total_photos_analyzed: int = 0,
        last_reset_date: date = None,
        username: str = None,
        first_name: str = None,
        last_name: str = None
    ):
        self.user_id = user_id
        self.created_at = created_at or datetime.now()
        self.language = language
        self.subscription_type = subscription_type
        self.subscription_until = subscription_until
        self.daily_photos_used = daily_photos_used
        self.total_photos_analyzed = total_photos_analyzed
        self.last_reset_date = last_reset_date or date.today()
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Создать User из словаря БД"""
        return cls(
            user_id=data['user_id'],
            created_at=data.get('created_at'),
            language=data.get('language', 'ru'),
            subscription_type=data.get('subscription_type', 'free'),
            subscription_until=data.get('subscription_until'),
            daily_photos_used=data.get('daily_photos_used', 0),
            total_photos_analyzed=data.get('total_photos_analyzed', 0),
            last_reset_date=data.get('last_reset_date', date.today()),
            username=data.get('username'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
    
    def to_dict(self) -> dict:
        """Конвертировать User в словарь для БД"""
        return {
            'user_id': self.user_id,
            'created_at': self.created_at,
            'language': self.language,
            'subscription_type': self.subscription_type,
            'subscription_until': self.subscription_until,
            'daily_photos_used': self.daily_photos_used,
            'total_photos_analyzed': self.total_photos_analyzed,
            'last_reset_date': self.last_reset_date,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name
        }
    
    def get_daily_limit(self) -> int:
        """Получить дневной лимит по типу подписки"""
        limits = {
            "free": 3,
            "premium_week": 10,
            "premium_month": 10
        }
        return limits.get(self.subscription_type, 3)
    
    def has_premium(self) -> bool:
        """Проверить активна ли премиум подписка"""
        if self.subscription_type == "free":
            return False
        
        if not self.subscription_until:
            return False
            
        return datetime.now() < self.subscription_until
    
    def get_remaining_photos(self) -> int:
        """Получить оставшееся количество фото на сегодня"""
        return max(0, self.get_daily_limit() - self.daily_photos_used)
    
    def can_analyze_photo(self) -> bool:
        """Может ли пользователь анализировать фото"""
        return self.get_remaining_photos() > 0
    
    def reset_daily_counter(self):
        """Сбросить дневной счетчик"""
        self.daily_photos_used = 0
        self.last_reset_date = date.today()