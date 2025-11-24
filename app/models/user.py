# app/models/user.py
@dataclass
class User:
    # ... поля ...
    
    def to_dict(self) -> dict:
        """Конвертирует User в dict для сохранения в БД"""
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
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Создает User из данных БД"""
        return cls(**data)