# app/handlers/photo_handler.py v1
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.services.gpt_analyzer import GPTAnalyzer
from app.core.i18n import get_localization
import logging
import os

logger = logging.getLogger(__name__)

photo_router = Router()
gpt_analyzer = GPTAnalyzer()

class PhotoAnalysis(StatesGroup):
    waiting_for_photo = State()
    waiting_for_description = State()

@photo_router.message(Command("analyze"))
async def cmd_analyze(message: Message, state: FSMContext):
    """Обработчик команды /analyze"""
    i18n = get_localization()
    await message.answer(i18n.get_text("send_photo_for_analysis"))
    await state.set_state(PhotoAnalysis.waiting_for_photo)

@photo_router.message(PhotoAnalysis.waiting_for_photo, F.photo)
async def handle_photo_with_state(message: Message, state: FSMContext):
    """Обрабатывает фото в состоянии анализа"""
    try:
        i18n = get_localization()
        
        # Сохраняем фото
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        file_path = f"temp_{message.from_user.id}.jpg"
        await message.bot.download_file(file.file_path, file_path)
        
        await state.update_data(photo_path=file_path)
        await message.answer(
            "📝 Хотите добавить описание к фото? Например: 'Салат с курицей и авокадо' или 'Домашняя пицца'\n\n"
            "Или просто отправьте 'нет' чтобы продолжить без описания",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(PhotoAnalysis.waiting_for_description)
        
    except Exception as e:
        logger.error(f"Ошибка обработки фото: {e}")
        await message.reply(i18n.get_text("analysis_error"))
        await state.clear()

@photo_router.message(PhotoAnalysis.waiting_for_description)
async def handle_description(message: Message, state: FSMContext):
    """Обрабатывает описание от пользователя"""
    try:
        i18n = get_localization()
        user_data = await state.get_data()
        photo_path = user_data.get('photo_path')
        
        if not photo_path:
            await message.reply("❌ Ошибка: фото не найдено")
            await state.clear()
            return
        
        user_description = None
        if message.text.lower() not in ['нет', 'no', 'skip']:
            user_description = message.text
        
        # Отправляем анализ
        wait_msg = await message.reply(i18n.get_text("analyzing_image"))
        
        # Анализируем фото через GPT с описанием
        analysis_result = await gpt_analyzer.analyze_food_image(
            photo_path, 
            user_description
        )
        
        # Удаляем временный файл
        if os.path.exists(photo_path):
            os.remove(photo_path)
        
        if analysis_result:
            await wait_msg.edit_text(analysis_result["analysis"])
        else:
            await wait_msg.edit_text(i18n.get_text("analysis_failed"))
            
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ошибка анализа: {e}")
        await message.reply(i18n.get_text("analysis_error"))
        await state.clear()

# Обработчик фото вне состояния (прямая отправка)
@photo_router.message(F.photo)
async def handle_photo_direct(message: Message, state: FSMContext):
    """Обрабатывает фото отправленное без команды /analyze"""
    await handle_photo_with_state(message, state)