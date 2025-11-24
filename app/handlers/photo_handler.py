# app/handlers/photo_handler.py
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, ContentType
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
    active_session = State()  # Состояние для накопления сообщений до анализа
    analysis_done = State()   # Состояние после анализа для уточнений

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

# ===== ЗАГРУЗКА ФОТО С ПОДПИСЬЮ ИЛИ БЕЗ =====
@food_photo_router.message(PhotoAnalysis.waiting_for_photo, F.photo)
async def handle_photo_with_caption(message: Message, state: FSMContext, user_service):  # ← ДОБАВИЛ user_service
    """Обрабатывает загрузку фото с подписью или без"""
    try:
        i18n = get_localization()
        user_id = message.from_user.id
        
        # 🔒 ПРОВЕРКА ЛИМИТОВ - ВОТ ГЛАВНОЕ ИЗМЕНЕНИЕ!
        if not await user_service.increment_photo_counter(user_id):
            # Лимит исчерпан
            limits_info = await user_service.get_user_limits_info(user_id)
            text = i18n.get_text("limit_exceeded").format(
                used=limits_info['photos_used'],
                limit=limits_info['photos_limit']
            )
            await message.answer(text, reply_markup=get_main_menu_keyboard())
            await state.clear()
            return
        
        # Получаем фото (самое качественное)
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        image_file = await message.bot.download_file(file.file_path)
        
        # Получаем подпись (caption), если есть
        caption = message.caption
        
        # Сохраняем file object и начинаем накапливать сообщения
        await state.update_data(
            image_file=image_file,
            user_messages=[caption] if caption else []  # Начинаем список сообщений
        )
        
        # Переходим к активной сессии
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

# ===== АКТИВНАЯ СЕССИЯ - накопление сообщений ДО анализа =====
@food_photo_router.message(PhotoAnalysis.active_session, F.text)
async def handle_active_session_text(message: Message, state: FSMContext):
    """Обрабатывает ЛЮБОЙ текст в активной сессии - накапливает сообщения"""
    i18n = get_localization()
    
    user_text = message.text
    user_data = await state.get_data()
    
    # Обработка кнопок
    if user_text == i18n.get_button_text("nutrition"):
        await process_analysis_request(message, state, "nutrition")
    elif user_text == i18n.get_button_text("recipe"):
        await process_analysis_request(message, state, "recipe")
    elif user_text == i18n.get_button_text("new_photo"):
        await handle_new_photo(message, state)
    elif user_text == i18n.get_button_text("cancel"):
        await handle_menu(message, state)
    else:
        # ЛЮБОЙ другой текст - добавляем в список сообщений (БЕЗ ответа)
        current_messages = user_data.get('user_messages', [])
        current_messages.append(user_text)
        
        await state.update_data(user_messages=current_messages)
        
        # Подсказка только после 3 сообщений
        messages_count = len(current_messages)
        if messages_count == 3:
            await message.answer(
                "💡 Я учел ваши замечания! Вы можете нажать '📊 Калорийность' или '👨‍🍳 Рецепт' для оценки блюда"
            )

# ===== СЕССИЯ ПОСЛЕ АНАЛИЗА - уточнения с ограничением =====
@food_photo_router.message(PhotoAnalysis.analysis_done, F.text)
async def handle_after_analysis_text(message: Message, state: FSMContext):
    """Обрабатывает текстовые сообщения ПОСЛЕ анализа - с ограничением 5 сообщений"""
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
        await handle_menu(message, state)
    else:
        # ЛЮБОЙ другой текст - отправляем как уточнение (с ограничением)
        await process_refinement_request(message, state, user_text)

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

async def handle_menu(message: Message, state: FSMContext):
    """Обрабатывает возврат в главное меню"""
    i18n = get_localization()
    
    # Очищаем сессию GPT
    if message.from_user.id in gpt_analyzer.user_sessions:
        del gpt_analyzer.user_sessions[message.from_user.id]
    
    await message.answer(
        i18n.get_text("cancel_success"),
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()

# ===== ОБРАБОТКА ФОТО БЕЗ КОМАНДЫ (с подписью или без) =====
@food_photo_router.message(F.photo)
async def handle_photo_direct(message: Message, state: FSMContext, user_service):  # ← ДОБАВИЛ user_service
    """Обрабатывает фото отправленное без команды"""
    await handle_photo_with_caption(message, state, user_service)  # ← ПЕРЕДАЛ user_service

# ===== ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ БЕЗ АКТИВНОЙ СЕССИИ =====
@food_photo_router.message(F.text)
async def handle_text_without_session(message: Message, state: FSMContext):
    """Обрабатывает текстовые сообщения, когда нет активной сессии с фото"""
    i18n = get_localization()
    
    user_text = message.text
    
    # Игнорируем команды и кнопки главного меню (они обрабатываются в basic_commands.py)
    if (user_text in ["📸 Анализировать еду", "❓ Помощь", "📊 Журнал", "👤 Профиль"] or 
        user_text.startswith('/')):
        return
    
    # Если пользователь просто пишет текст без фото - предлагаем загрузить фото
    await message.answer(
        "📸 Для анализа еды сначала отправьте фото, а затем можете написать уточнение текстом.\n\n"
        "Нажмите '📸 Анализировать еду' чтобы начать.",
        reply_markup=get_main_menu_keyboard()
    )

# ===== ОСНОВНАЯ ФУНКЦИЯ АНАЛИЗА =====
async def process_analysis_request(message: Message, state: FSMContext, analysis_type: str):
    """Общая функция для обработки всех типов анализа (первый запрос)"""
    try:
        i18n = get_localization()
        user_data = await state.get_data()
        
        # Получаем фото и накопленные сообщения
        image_file = user_data.get('image_file')
        user_messages = user_data.get('user_messages', [])
        
        if not image_file:
            await message.answer(
                "❌ Ошибка: фото не найдено",
                reply_markup=get_main_menu_keyboard()
            )
            await state.clear()
            return
        
        # Объединяем все сообщения в один текст
        combined_message = None
        if user_messages:
            combined_message = "\n".join(user_messages)
            print(f"🔍 DEBUG: Объединенные сообщения: {combined_message}")
        
        # Отправляем сообщение о начале анализа
        wait_msg = await message.answer(i18n.get_text("analyzing_image"))
        
        # Анализируем через GPT
        analysis_result = await gpt_analyzer.analyze_food_image(
            user_id=message.from_user.id,
            image_file=image_file,
            analysis_type=analysis_type,
            user_message=combined_message
        )
        
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
        
        # Переходим в состояние "анализ выполнен"
        await state.set_state(PhotoAnalysis.analysis_done)
        
        # Очищаем накопленные сообщения после успешного анализа
        await state.update_data(user_messages=[])
        
        # Показываем сколько сообщений осталось
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

# ===== ФУНКЦИЯ ДЛЯ УТОЧНЕНИЙ ПОСЛЕ АНАЛИЗА =====
async def process_refinement_request(message: Message, state: FSMContext, user_message: str):
    """Обрабатывает уточнения после анализа (с ограничением)"""
    try:
        i18n = get_localization()
        
        # Отправляем сообщение о начале анализа
        wait_msg = await message.answer(i18n.get_text("analyzing_image"))
        
        # Определяем тип анализа на основе текущего состояния
        # Если пользователь ранее запрашивал рецепт - продолжаем рецепт
        current_state = await state.get_state()
        analysis_type = "nutrition"  # по умолчанию
        
        # Анализируем через GPT (без фото, только уточнение)
        analysis_result = await gpt_analyzer.analyze_food_image(
            user_id=message.from_user.id,
            image_file=None,  # Без фото, только уточнение
            analysis_type=analysis_type,
            user_message=user_message
        )
        
        # 🔧 ПРОВЕРКА РЕЗУЛЬТАТА
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
        logger.error(f"Ошибка уточнения: {e}")
        await message.answer(
            i18n.get_text("analysis_error"),
            reply_markup=get_main_menu_keyboard()
        )