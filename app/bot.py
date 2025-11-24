import os
import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.handlers import router
from app.locales.base import localization_manager
from app.database import Database
from app.services import UserService

# Импорты для Модуля 4
from app.middlewares.limit_middleware import LimitMiddleware


def setup_logging():
    """Настройка логирования"""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    return logging.getLogger(__name__)


def setup_localization():
    """Настройка локализации"""
    default_lang = os.getenv('DEFAULT_LANGUAGE', 'ru')
    localization_manager.default_lang = default_lang
    logging.getLogger(__name__).info(f"Локализация установлена: {default_lang}")


async def main():
    """Основная функция для запуска бота"""
    # Загружаем переменные окружения
    load_dotenv()
    
    # Настраиваем логирование
    logger = setup_logging()
    
    # Настраиваем локализацию
    setup_localization()
    
    # Проверяем наличие токена
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        logger.error("BOT_TOKEN не найден в .env файле!")
        return
    
    logger.info(f"Токен бота: {bot_token[:10]}...")  # Логируем часть токена для проверки
    
    # Инициализация БД и сервисов
    try:
        database = Database(os.getenv('DATABASE_URL'))
        await database.init_db()
        logger.info("✅ База данных инициализирована")
        
        user_service = UserService(database)
        logger.info("✅ Сервисы инициализированы")
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        return
    
    # Инициализация бота и диспетчера
    try:
        bot = Bot(token=bot_token)
        logger.info("Бот инициализирован")
        
        storage = MemoryStorage()
        
        # Создаем диспетчер и передаем сервисы
        dp = Dispatcher(storage=storage, user_service=user_service)
        logger.info("Диспетчер инициализирован")
        
        # ===== ДОБАВЛЯЕМ MIDDLEWARE ДЛЯ ЛИМИТОВ =====
        dp.update.middleware(LimitMiddleware())
        logger.info("✅ Middleware лимитов подключен")
        
        # ===== РЕГИСТРАЦИЯ ВСЕХ РОУТЕРОВ =====
        dp.include_router(router)  # Основные обработчики
        #dp.include_router(admin_handlers.router)  # Административные команды
        logger.info("✅ Все роутеры зарегистрированы")

        # Получаем информацию о боте
        bot_info = await bot.get_me()
        logger.info(f"Бот запущен: @{bot_info.username} ({bot_info.first_name})")
        
        # Запуск опроса
        logger.info("Начинаем опрос...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise
    finally:
        if 'bot' in locals():
            await bot.session.close()
            logger.info("Сессия бота закрыта")


if __name__ == "__main__":
    asyncio.run(main())