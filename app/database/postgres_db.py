# app/database/postgres_db.py
from typing import Optional, Dict, Any
import asyncpg
import os
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
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Возвращает сырые данные пользователя как словарь"""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                'SELECT * FROM users WHERE user_id = $1', 
                user_id
            )
            return dict(row) if row else None
    
    async def save_user(self, user_data: Dict[str, Any]):
        """Сохраняет данные пользователя из словаря"""
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
                user_data['user_id'], 
                user_data['created_at'], 
                user_data['language'],
                user_data['subscription_type'], 
                user_data['subscription_until'],
                user_data['daily_photos_used'], 
                user_data['daily_texts_used'],
                user_data['last_reset_date'], 
                user_data['custom_photo_limit'],
                user_data['custom_text_limit']
            ))