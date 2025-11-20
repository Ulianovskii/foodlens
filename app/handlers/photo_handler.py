from aiogram import F, Router
from aiogram.types import Message
import logging

from app.locales import get_text

# Создаем роутер для обработки фотографий
photo_router = Router()
logger = logging.getLogger(__name__)


@photo_router.message(F.photo)
async def handle_photo(message: Message):
    """
    Базовый обработчик фотографий для Модуля 2.
    В Модуле 3 будет заменен на полноценную реализацию анализа.
    """
    logger.info(f"Получено фото от пользователя {message.from_user.id}")
    
    text = get_text('photo_received')
    await message.answer(text)
    
    # Можно добавить сохранение фото для тестирования
    try:
        # В будущем здесь будет сохранение и обработка фото
        photo = message.photo[-1]
        logger.info(f"Размер фото: {photo.file_size} bytes")
    except Exception as e:
        logger.error(f"Ошибка при обработке фото: {e}")


@photo_router.message(F.document)
async def handle_document(message: Message):
    """
    Обработчик документов (на случай, если отправят файл вместо фото)
    """
    text = get_text('document_received')
    await message.answer(text)