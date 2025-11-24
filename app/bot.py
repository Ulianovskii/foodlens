import os
import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.handlers import router
from app.locales.base import localization_manager

async def main():
    # Инициализация БД
    database = Database(os.getenv('DATABASE_URL'))
    await database.init_db()
    
    # Инициализация сервисов
    user_service = UserService(database)
    
    # Запуск бота с зависимостями
    await dp.start_polling(bot, user_service=user_service)

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
    
    # Инициализация бота и диспетчера
    try:
        bot = Bot(token=bot_token)
        logger.info("Бот инициализирован")
        
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        logger.info("Диспетчер инициализирован")
        
        # Регистрация роутера с обработчиками
        dp.include_router(router)
        logger.info("Роутеры зарегистрированы")

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