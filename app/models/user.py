# app/models/user.py
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Dict

@dataclass
class User:
    user_id: int
    created_at: datetime
    language: str = "ru"
    
    # Система лимитов
    subscription_type: str = "free"  # free/premium_week/premium_month
    subscription_until: Optional[datetime] = None
    daily_photos_used: int = 0
    daily_texts_used: int = 0
    last_reset_date: Optional[date] = None
    
    # Кастомные лимиты (для админов и тестов)
    custom_photo_limit: Optional[int] = None
    custom_text_limit: Optional[int] = None
    
    # Методы для работы с лимитами
    def get_photo_limit(self) -> int:
        if self.custom_photo_limit:
            return self.custom_photo_limit
        
        limits = {
            "free": 3,
            "premium_week": 10,
            "premium_month": 10
        }
        return limits.get(self.subscription_type, 3)
    
    def get_text_limit(self) -> int:
        if self.custom_text_limit:
            return self.custom_text_limit
            
        limits = {
            "free": 10,
            "premium_week": 30,
            "premium_month": 30
        }
        return limits.get(self.subscription_type, 10)
    
    def has_photo_quota(self) -> bool:
        return self.daily_photos_used < self.get_photo_limit()
    
    def has_text_quota(self) -> bool:
        return self.daily_texts_used < self.get_text_limit()
    
    def is_premium(self) -> bool:
        if self.subscription_type == "free":
            return False
        if self.subscription_until and self.subscription_until < datetime.now():
            return False
        return True