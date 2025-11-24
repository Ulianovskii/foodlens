#app/models/user.py
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
        
    def get_daily_limit(self) -> int:
        """Возвращает дневной лимит в зависимости от подписки"""
        if self.subscription_type in ["premium_week", "premium_month"]:
            return 10
        return 3
    
    def can_analyze_photo(self) -> bool:
        """Может ли пользователь анализировать фото"""
        return self.daily_photos_used < self.get_daily_limit()
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
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
        )
    
    def to_dict(self) -> dict:
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
        }