# app/handlers/photo_handler.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from app.services.gpt_analyzer import GPTAnalyzer
from app.core.i18n import get_localization
import logging
import os

logger = logging.getLogger(__name__)

router = Router()
gpt_analyzer = GPTAnalyzer()

@router.message(F.photo)
async def handle_photo_message(message: Message):
    """Обрабатывает фото от пользователя"""
    try:
        # Получаем локализацию
        i18n = get_localization()
        
        # Отправляем сообщение о начале анализа
        wait_msg = await message.reply(i18n.get_text("analyzing_image"))
        
        # Скачиваем фото
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        file_path = f"temp_{message.from_user.id}.jpg"
        await message.bot.download_file(file.file_path, file_path)
        
        # Анализируем фото через GPT
        analysis_result = await gpt_analyzer.analyze_food_image(file_path)
        
        # Удаляем временный файл
        if os.path.exists(file_path):
            os.remove(file_path)
        
        if analysis_result:
            await wait_msg.edit_text(analysis_result["analysis"])
        else:
            await wait_msg.edit_text(i18n.get_text("analysis_failed"))
            
    except Exception as e:
        logger.error(f"Ошибка обработки фото: {e}")
        i18n = get_localization()
        await message.reply(i18n.get_text("analysis_error"))

@router.message(Command("analyze"))
async def cmd_analyze(message: Message):
    """Обработчик команды /analyze"""
    i18n = get_localization()
    await message.answer(i18n.get_text("send_photo_for_analysis"))