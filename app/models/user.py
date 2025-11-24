# app/models/user.py - ИСПРАВЛЕННЫЙ
from dataclasses import dataclass  # ← ДОБАВИТЬ ЭТОТ ИМПОРТ!
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
        """Создает User из данных БД"""
        return cls(**data)