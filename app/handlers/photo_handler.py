# app/handlers/photo_handler.py
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.services.gpt_analyzer import GPTAnalyzer
from app.core.i18n import get_localization
from app.keyboards.main_menu import get_main_menu_keyboard
from app.keyboards.analysis_menu import get_analysis_menu_keyboard
import logging

logger = logging.getLogger(__name__)

food_photo_router = Router()
gpt_analyzer = GPTAnalyzer()

class PhotoAnalysis(StatesGroup):
    waiting_for_photo = State()
    active_session = State()  # Новое состояние - активная сессия

# ===== ОСНОВНОЕ МЕНЮ =====
@food_photo_router.message(F.text == "📸 Анализировать еду")
@food_photo_router.message(Command("analyze"))
async def cmd_analyze(message: Message, state: FSMContext):
    """Обработчик команды /analyze или кнопки анализа"""
    i18n = get_localization()
    
    # Очищаем старые сессии
    gpt_analyzer.cleanup_sessions()
    
    await message.answer(
        i18n.get_text("send_photo_for_analysis"),
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(PhotoAnalysis.waiting_for_photo)

# ===== ЗАГРУЗКА ФОТО =====
@food_photo_router.message(PhotoAnalysis.waiting_for_photo, F.photo)
async def handle_photo(message: Message, state: FSMContext):
    """Обрабатывает загрузку фото"""
    try:
        i18n = get_localization()
        
        # Получаем фото (самое качественное)
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        image_file = await message.bot.download_file(file.file_path)
        
        # Сохраняем file object в состоянии
        await state.update_data(image_file=image_file)
        
        # СРАЗУ переходим к активной сессии
        await message.answer(
            i18n.get_text("photo_received_options"),
            reply_markup=get_analysis_menu_keyboard()
        )
        await state.set_state(PhotoAnalysis.active_session)
        
    except Exception as e:
        logger.error(f"Ошибка загрузки фото: {e}")
        await message.answer(
            i18n.get_text("analysis_error"),
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()

# ===== АКТИВНАЯ СЕССИЯ - обработка ВСЕХ сообщений =====
@food_photo_router.message(PhotoAnalysis.active_session, F.text)
async def handle_active_session_text(message: Message, state: FSMContext):
    """Обрабатывает ЛЮБОЙ текст в активной сессии"""
    i18n = get_localization()
    
    user_text = message.text
    
    # Обработка кнопок
    if user_text == i18n.get_button_text("nutrition"):
        await process_analysis_request(message, state, "nutrition")
    elif user_text == i18n.get_button_text("recipe"):
        await process_analysis_request(message, state, "recipe")
    elif user_text == i18n.get_button_text("new_photo"):
        await handle_new_photo(message, state)
    elif user_text == i18n.get_button_text("cancel"):
        await handle_cancel(message, state)
    else:
        # ЛЮБОЙ другой текст - отправляем как уточнение/вопрос к текущему фото
        await process_analysis_request(message, state, "refinement", user_message=user_text)

# ===== ОБРАБОТКА КНОПОК =====
async def handle_new_photo(message: Message, state: FSMContext):
    """Обрабатывает запрос нового фото"""
    i18n = get_localization()
    
    # Очищаем сессию GPT
    if message.from_user.id in gpt_analyzer.user_sessions:
        del gpt_analyzer.user_sessions[message.from_user.id]
    
    await message.answer(
        i18n.get_text("send_photo_for_analysis"),
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(PhotoAnalysis.waiting_for_photo)

async def handle_cancel(message: Message, state: FSMContext):
    """Обрабатывает отмену"""
    i18n = get_localization()
    
    # Очищаем сессию GPT
    if message.from_user.id in gpt_analyzer.user_sessions:
        del gpt_analyzer.user_sessions[message.from_user.id]
    
    await message.answer(
        i18n.get_text("cancel_success"),
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()

# ===== ОБРАБОТКА ФОТО БЕЗ КОМАНДЫ =====
@food_photo_router.message(F.photo)
async def handle_photo_direct(message: Message, state: FSMContext):
    """Обрабатывает фото отправленное без команды"""
    await handle_photo(message, state)

# ===== ОСНОВНАЯ ФУНКЦИЯ АНАЛИЗА =====
async def process_analysis_request(message: Message, state: FSMContext, analysis_type: str, user_message: str = None):
    """Общая функция для обработки всех типов анализа"""
    try:
        i18n = get_localization()
        user_data = await state.get_data()
        
        # Для первого запроса нужен файл фото
        image_file = user_data.get('image_file') if analysis_type != "refinement" else None
        
        # Отправляем сообщение о начале анализа
        wait_msg = await message.answer(i18n.get_text("analyzing_image"))
        
        # Анализируем через GPT
        analysis_result = await gpt_analyzer.analyze_food_image(
            user_id=message.from_user.id,
            image_file=image_file,
            analysis_type=analysis_type,
            user_message=user_message
        )  # ⚠️ ЗАКРЫВАЕМ СКОБКУ И УБИРАЕМ ЛИШНИЙ КОД
        
        # 🔧 ПРОВЕРКА РЕЗУЛЬТАТА
        if analysis_result is None:
            await wait_msg.edit_text(i18n.get_text("analysis_failed"))
            await message.answer(
                "Попробуйте еще раз",
                reply_markup=get_main_menu_keyboard()
            )
            await state.clear()
            return
            
        if analysis_result.get("error"):
            if analysis_result.get("error") == "message_limit_reached":
                await wait_msg.edit_text(i18n.get_text("message_limit_reached"))
                await message.answer(
                    i18n.get_text("send_photo_for_analysis"),
                    reply_markup=get_main_menu_keyboard()
                )
                await state.clear()
                return
            else:
                await wait_msg.edit_text(i18n.get_text("analysis_failed"))
                await state.clear()
                return
        
        # Показываем результат
        await wait_msg.edit_text(analysis_result["analysis"])
        
        # Показываем сколько сообщений осталось
        messages_left = analysis_result.get("messages_left", 5)
        if messages_left > 0:
            await message.answer(
                i18n.get_text("messages_left", count=messages_left),
                reply_markup=get_analysis_menu_keyboard()
            )
        else:
            await message.answer(
                i18n.get_text("message_limit_reached"),
                reply_markup=get_main_menu_keyboard()
            )
            await state.clear()
            
    except Exception as e:
        logger.error(f"Ошибка анализа: {e}")
        await message.answer(
            i18n.get_text("analysis_error"),
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()