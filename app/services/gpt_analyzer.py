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

router = Router()
gpt_analyzer = GPTAnalyzer()

class PhotoAnalysis(StatesGroup):
    waiting_for_photo = State()
    active_session = State()
    analysis_done = State()

# ===== ОСНОВНОЕ МЕНЮ =====
@router.message(F.text == get_localization().get_button_text('analyze_food'))
@router.message(Command("analyze"))
async def cmd_analyze(message: Message, state: FSMContext):
    """Обработчик команды /analyze или кнопки анализа"""
    i18n = get_localization()
    
    gpt_analyzer.cleanup_sessions()
    
    await message.answer(
        i18n.get_text("send_photo_for_analysis"),
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(PhotoAnalysis.waiting_for_photo)

# ===== ЗАГРУЗКА ФОТО =====
@router.message(PhotoAnalysis.waiting_for_photo, F.photo)
async def handle_photo_with_caption(message: Message, state: FSMContext):
    """Обрабатывает загрузку фото с подписью или без"""
    try:
        i18n = get_localization()
        
        user_id = message.from_user.id
        if user_id in gpt_analyzer.user_sessions:
            del gpt_analyzer.user_sessions[user_id]
            print(f"🔍 DEBUG: Очищена старая сессия GPT для пользователя {user_id}")
        
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        image_file = await message.bot.download_file(file.file_path)
        
        caption = message.caption
        
        await state.update_data(
            image_file=image_file,
            user_messages=[caption] if caption else []
        )
        
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

# ===== АКТИВНАЯ СЕССИЯ =====
@router.message(PhotoAnalysis.active_session, F.text)
async def handle_active_session_text(message: Message, state: FSMContext):
    """Обрабатывает текст в активной сессии"""
    i18n = get_localization()
    
    user_text = message.text
    user_data = await state.get_data()
    
    if user_text == i18n.get_button_text("nutrition"):
        await process_analysis_request(message, state, "nutrition")
    elif user_text == i18n.get_button_text("recipe"):
        await process_analysis_request(message, state, "recipe")
    elif user_text == i18n.get_button_text("new_photo"):
        await handle_new_photo(message, state)
    elif user_text == i18n.get_button_text("cancel"):
        await handle_menu(message, state)
    else:
        current_messages = user_data.get('user_messages', [])
        current_messages.append(user_text)
        
        await state.update_data(user_messages=current_messages)
        
        messages_count = len(current_messages)
        if messages_count == 3:
            await message.answer(i18n.get_text('refinement_hint'))

# ===== СЕССИЯ ПОСЛЕ АНАЛИЗА =====
@router.message(PhotoAnalysis.analysis_done, F.text)
async def handle_after_analysis_text(message: Message, state: FSMContext):
    """Обрабатывает текстовые сообщения ПОСЛЕ анализа"""
    i18n = get_localization()
    
    user_text = message.text
    
    if user_text == i18n.get_button_text("nutrition"):
        await process_analysis_request(message, state, "nutrition")
    elif user_text == i18n.get_button_text("recipe"):
        await process_analysis_request(message, state, "recipe")
    elif user_text == i18n.get_button_text("new_photo"):
        await handle_new_photo(message, state)
    elif user_text == i18n.get_button_text("cancel"):
        await handle_menu(message, state)
    else:
        await process_refinement_request(message, state, user_text)

# ===== ОБРАБОТКА КНОПОК =====
async def handle_new_photo(message: Message, state: FSMContext):
    """Обрабатывает запрос нового фото"""
    i18n = get_localization()
    
    user_id = message.from_user.id
    if user_id in gpt_analyzer.user_sessions:
        del gpt_analyzer.user_sessions[user_id]
        print(f"🔍 DEBUG: Очищена сессия GPT для пользователя {user_id}")
    
    await message.answer(
        i18n.get_text("send_photo_for_analysis"),
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(PhotoAnalysis.waiting_for_photo)

async def handle_menu(message: Message, state: FSMContext):
    """Обрабатывает возврат в главное меню"""
    i18n = get_localization()
    
    user_id = message.from_user.id
    if user_id in gpt_analyzer.user_sessions:
        del gpt_analyzer.user_sessions[user_id]
    
    await message.answer(
        i18n.get_text("cancel_success"),
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()

# ===== ОБРАБОТКА ФОТО БЕЗ КОМАНДЫ =====
@router.message(F.photo)
async def handle_photo_direct(message: Message, state: FSMContext):
    """Обрабатывает фото отправленное без команды"""
    user_id = message.from_user.id
    if user_id in gpt_analyzer.user_sessions:
        del gpt_analyzer.user_sessions[user_id]
        print(f"🔍 DEBUG: Очищена старая сессия GPT для пользователя {user_id}")
    
    await handle_photo_with_caption(message, state)

# ===== ТЕКСТ БЕЗ СЕССИИ =====
@router.message(F.text)
async def handle_text_without_session(message: Message, state: FSMContext):
    """Обрабатывает текстовые сообщения без активной сессии"""
    i18n = get_localization()
    
    user_text = message.text
    
    main_menu_buttons = [
        i18n.get_button_text('analyze_food'),
        i18n.get_button_text('help'),
        i18n.get_button_text('history'),
        i18n.get_button_text('profile')
    ]
    
    if user_text in main_menu_buttons or user_text.startswith('/'):
        return
    
    await message.answer(
        i18n.get_text('photo_first_then_text'),
        reply_markup=get_main_menu_keyboard()
    )

# ===== ОСНОВНАЯ ФУНКЦИЯ АНАЛИЗА =====
async def process_analysis_request(message: Message, state: FSMContext, analysis_type: str):
    """Общая функция для обработки анализа"""
    try:
        i18n = get_localization()
        user_data = await state.get_data()
        
        image_file = user_data.get('image_file')
        user_messages = user_data.get('user_messages', [])
        
        if not image_file:
            await message.answer(
                i18n.get_text('photo_not_found'),
                reply_markup=get_main_menu_keyboard()
            )
            await state.clear()
            return
        
        combined_message = None
        if user_messages:
            combined_message = "\n".join(user_messages)
            print(f"🔍 DEBUG: Объединенные сообщения: {combined_message}")
        
        wait_msg = await message.answer(i18n.get_text("analyzing_image"))
        
        analysis_result = await gpt_analyzer.analyze_food_image(
            user_id=message.from_user.id,
            image_file=image_file,
            analysis_type=analysis_type,
            user_message=combined_message
        )
        
        if analysis_result is None:
            await wait_msg.edit_text(i18n.get_text("analysis_failed"))
            await message.answer(
                i18n.get_text('try_again'),
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
        
        await wait_msg.edit_text(analysis_result["analysis"])
        await state.set_state(PhotoAnalysis.analysis_done)
        await state.update_data(user_messages=[])
        
        messages_left = analysis_result.get("messages_left", 5)
        await message.answer(
            i18n.get_text("messages_left", count=messages_left),
            reply_markup=get_analysis_menu_keyboard()
        )
            
    except Exception as e:
        logger.error(f"Ошибка анализа: {e}")
        await message.answer(
            i18n.get_text("analysis_error"),
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()

# ===== ФУНКЦИЯ ДЛЯ УТОЧНЕНИЙ =====
async def process_refinement_request(message: Message, state: FSMContext, user_message: str):
    """Обрабатывает уточнения после анализа"""
    try:
        i18n = get_localization()
        
        wait_msg = await message.answer(i18n.get_text("analyzing_image"))
        
        analysis_type = "nutrition"
        
        analysis_result = await gpt_analyzer.analyze_food_image(
            user_id=message.from_user.id,
            image_file=None,
            analysis_type=analysis_type,
            user_message=user_message
        )
        
        if analysis_result is None:
            await wait_msg.edit_text(i18n.get_text("analysis_failed"))
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
        
        await wait_msg.edit_text(analysis_result["analysis"])
        
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
        logger.error(f"Ошибка уточнения: {e}")
        await message.answer(
            i18n.get_text("analysis_error"),
            reply_markup=get_main_menu_keyboard()
        )