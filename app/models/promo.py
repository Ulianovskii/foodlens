from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

class PromoType(Enum):
    PREMIUM_WEEK = "premium_week"
    PREMIUM_MONTH = "premium_month"

class PromoCode:
    def __init__(
        self,
        code: str,
        promo_type: str,
        is_used: bool = False,
        used_by: Optional[int] = None,
        used_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        id: Optional[int] = None
    ):
        self.id = id
        self.code = code
        self.promo_type = promo_type
        self.is_used = is_used
        self.used_by = used_by
        self.used_at = used_at
        self.created_at = created_at or datetime.now()
        self.expires_at = expires_at
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PromoCode':
        """Создать PromoCode из словаря БД"""
        return cls(
            id=data.get('id'),
            code=data['code'],
            promo_type=data['promo_type'],
            is_used=data.get('is_used', False),
            used_by=data.get('used_by'),
            used_at=data.get('used_at'),
            created_at=data.get('created_at'),
            expires_at=data.get('expires_at')
        )
    
    def to_dict(self) -> dict:
        """Конвертировать PromoCode в словарь для БД"""
        return {
            'id': self.id,
            'code': self.code,
            'promo_type': self.promo_type,
            'is_used': self.is_used,
            'used_by': self.used_by,
            'used_at': self.used_at,
            'created_at': self.created_at,
            'expires_at': self.expires_at
        }
    
    def is_valid(self) -> bool:
        """Проверить валидность промокода"""
        if self.is_used:
            return False
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        return True
    
    def get_subscription_days(self) -> int:
        """Получить количество дней подписки"""
        return 30 if self.promo_type == PromoType.PREMIUM_MONTH.value else 7