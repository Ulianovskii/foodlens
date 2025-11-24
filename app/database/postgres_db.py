#app/database/postgres_db.py 
from typing import Optional, Dict, Any, List
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
            await self._create_tables()  # Всегда создаем/проверяем таблицы
            pool = await self.get_pool()
            async with pool.acquire() as conn:
                await conn.execute("SELECT 1 FROM users LIMIT 1")
            logger.info("✅ База данных подключена и готова к работе")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации БД: {e}")
            raise
    
    async def get_user(self, user_id: int) -> Optional[dict]:
        """Возвращает сырые данные пользователя как словарь"""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                'SELECT * FROM users WHERE user_id = $1', 
                user_id
            )
            return dict(row) if row else None
    
    async def save_user(self, user_data: dict):
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO users 
                (user_id, username, created_at, language, subscription_type, 
                subscription_until, daily_photos_used, total_photos_analyzed, last_reset_date)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (user_id) DO UPDATE SET
                    username = EXCLUDED.username,
                    language = EXCLUDED.language,
                    subscription_type = EXCLUDED.subscription_type,
                    subscription_until = EXCLUDED.subscription_until,
                    daily_photos_used = EXCLUDED.daily_photos_used,
                    total_photos_analyzed = EXCLUDED.total_photos_analyzed,
                    last_reset_date = EXCLUDED.last_reset_date,
                    updated_at = NOW()
            ''', 
                user_data['user_id'],
                user_data.get('username'),
                user_data['created_at'], 
                user_data.get('language', 'ru'),
                user_data.get('subscription_type', 'free'), 
                user_data.get('subscription_until'),
                user_data.get('daily_photos_used', 0),
                user_data.get('total_photos_analyzed', 0),
                user_data.get('last_reset_date')
            )

    async def _create_tables(self):
        """Создание таблиц если их нет"""
        try:
            pool = await self.get_pool()
            async with pool.acquire() as conn:
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY,
                        username VARCHAR(100),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        language VARCHAR(10) DEFAULT 'ru',
                        subscription_type VARCHAR(20) DEFAULT 'free',
                        subscription_until TIMESTAMP WITH TIME ZONE,
                        daily_photos_used INTEGER DEFAULT 0,
                        total_photos_analyzed INTEGER DEFAULT 0,
                        last_reset_date DATE DEFAULT CURRENT_DATE,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                ''')
                
                # Создаем таблицу промокодов
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS promo_codes (
                        id SERIAL PRIMARY KEY,
                        code VARCHAR(50) UNIQUE NOT NULL,
                        promo_type VARCHAR(20) NOT NULL,
                        is_used BOOLEAN DEFAULT FALSE,
                        used_by BIGINT,
                        used_at TIMESTAMP WITH TIME ZONE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        expires_at TIMESTAMP WITH TIME ZONE
                    )
                ''')
                logger.info("✅ Таблицы users и promo_codes созданы/проверены")
        except Exception as e:
            logger.error(f"❌ Ошибка создания таблиц: {e}")
            raise

    # МЕТОДЫ ДЛЯ ПРОМОКОДОВ
    
    async def save_promo_code(self, promo_data: dict):
        """Сохранить промокод в БД"""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO promo_codes 
                (code, promo_type, expires_at)
                VALUES ($1, $2, $3)
            ''', 
                promo_data['code'],
                promo_data['promo_type'],
                promo_data.get('expires_at')
            )

    async def get_promo_code(self, code: str) -> Optional[dict]:
        """Получить промокод по коду"""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                'SELECT * FROM promo_codes WHERE code = $1', 
                code
            )
            return dict(row) if row else None

    async def mark_promo_code_used(self, code: str, user_id: int):
        """Пометить промокод как использованный"""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            await conn.execute('''
                UPDATE promo_codes 
                SET is_used = TRUE, used_by = $1, used_at = NOW()
                WHERE code = $2
            ''', user_id, code)

    async def get_all_promo_codes(self) -> List[dict]:
        """Получить все промокоды"""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM promo_codes ORDER BY created_at DESC')
            return [dict(row) for row in rows]

    async def reset_promo_codes(self):
        """Удалить все промокоды (для тестирования)"""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            await conn.execute('DELETE FROM promo_codes')