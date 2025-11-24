# app/database/postgres_db.py v1 - ИСПРАВЛЕННАЯ
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
        """Проверка подключения к БД и инициализация"""
        try:
            pool = await self.get_pool()
            async with pool.acquire() as conn:
                # Проверяем что таблица существует
                await conn.execute("SELECT 1 FROM users LIMIT 1")
            logger.info("✅ База данных подключена и готова к работе")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации БД: {e}")
            # Если таблицы нет - создаем (на время разработки)
            await self._create_tables()
    
    # app/database/postgres_db.py - исправить метод get_user
    async def get_user(self, user_id: int) -> Optional[dict]:
        """Возвращает сырые данные пользователя как словарь"""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                'SELECT * FROM users WHERE user_id = $1', 
                user_id
            )
            return dict(row) if row else None
    
   # app/database/postgres_db.py - ИСПРАВЛЕННЫЙ метод save_user
    async def save_user(self, user_data: dict):
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO users 
                (user_id, created_at, language, subscription_type, 
                subscription_until, daily_photos_used, daily_texts_used,
                last_reset_date, custom_photo_limit, custom_text_limit)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ON CONFLICT (user_id) DO UPDATE SET
                    language = EXCLUDED.language,
                    subscription_type = EXCLUDED.subscription_type,
                    subscription_until = EXCLUDED.subscription_until,
                    daily_photos_used = EXCLUDED.daily_photos_used,
                    daily_texts_used = EXCLUDED.daily_texts_used,
                    last_reset_date = EXCLUDED.last_reset_date,
                    custom_photo_limit = EXCLUDED.custom_photo_limit,
                    custom_text_limit = EXCLUDED.custom_text_limit,
                    updated_at = NOW()
            ''', (
                user_data.get('user_id'), 
                user_data.get('created_at'), 
                user_data.get('language', 'ru'),
                user_data.get('subscription_type', 'free'), 
                user_data.get('subscription_until'),
                user_data.get('daily_photos_used', 0), 
                user_data.get('daily_texts_used', 0),
                user_data.get('last_reset_date'), 
                user_data.get('custom_photo_limit'),
                user_data.get('custom_text_limit')
            ))
    
    async def _create_tables(self):
        """Создание таблиц если их нет"""  # ← ДОБАВЛЕН ОТСТУП!
        try:
            pool = await self.get_pool()
            async with pool.acquire() as conn:
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        language VARCHAR(10) DEFAULT 'ru',
                        subscription_type VARCHAR(20) DEFAULT 'free',
                        subscription_until TIMESTAMP WITH TIME ZONE,
                        daily_photos_used INTEGER DEFAULT 0,
                        daily_texts_used INTEGER DEFAULT 0,
                        last_reset_date DATE,
                        custom_photo_limit INTEGER,
                        custom_text_limit INTEGER,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                ''')
                logger.info("✅ Таблица users создана")
        except Exception as e:
            logger.error(f"❌ Ошибка создания таблиц: {e}")
            raise