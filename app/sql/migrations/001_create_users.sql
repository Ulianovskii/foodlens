# app/database/postgres_db.py
import asyncpg
from datetime import datetime, date
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._pool = None
    
    async def get_pool(self):
        if not self._pool:
            self._pool = await asyncpg.create_pool(self.connection_string)
        return self._pool
    
    async def init_db(self):
        """Инициализация таблиц (миграции через Docker)"""
        pool = await self.get_pool()
        # Таблицы создаются через миграции в Docker
        logger.info("База данных инициализирована")
    
    async def get_user(self, user_id: int) -> User:
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                'SELECT * FROM users WHERE user_id = $1', 
                user_id
            )
            
            if row:
                return self._row_to_user(row)
            return None
    
    async def save_user(self, user: User):
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO users 
                (user_id, created_at, language, subscription_type, 
                 subscription_until, daily_photos_used, daily_texts_used,
                 last_reset_date, custom_photo_limit, custom_text_limit)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ON CONFLICT (user_id) DO UPDATE SET
                    language = $3,
                    subscription_type = $4,
                    subscription_until = $5,
                    daily_photos_used = $6,
                    daily_texts_used = $7,
                    last_reset_date = $8,
                    custom_photo_limit = $9,
                    custom_text_limit = $10,
                    updated_at = NOW()
            ''', (
                user.user_id, user.created_at, user.language,
                user.subscription_type, user.subscription_until,
                user.daily_photos_used, user.daily_texts_used,
                user.last_reset_date, user.custom_photo_limit,
                user.custom_text_limit
            ))
    
    def _row_to_user(self, row) -> User:
        """Конвертирует строку БД в объект User"""
        return User(
            user_id=row['user_id'],
            created_at=row['created_at'],
            language=row['language'],
            subscription_type=row['subscription_type'],
            subscription_until=row['subscription_until'],
            daily_photos_used=row['daily_photos_used'],
            daily_texts_used=row['daily_texts_used'],
            last_reset_date=row['last_reset_date'],
            custom_photo_limit=row['custom_photo_limit'],
            custom_text_limit=row['custom_text_limit']
        )