from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from app.services.user_service import UserService
from app.core.i18n import get_localization
from app.keyboards.main_menu import get_main_menu_keyboard
from app.keyboards.inline_menus import get_profile_keyboard, get_premium_menu_keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    i18n = get_localization()
    
    await message.answer(
        f"{i18n.get_text('start_welcome')}\n\n",
        reply_markup=get_main_menu_keyboard()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    i18n = get_localization()
    await message.answer(
        i18n.get_text('help_text'),
        reply_markup=get_main_menu_keyboard()
    )

@router.message(Command("cancel"))
async def cmd_cancel(message: Message):
    i18n = get_localization()
    await message.answer(
        i18n.get_text('cancel_success'),
        reply_markup=get_main_menu_keyboard()
    )

@router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Команда для возврата в главное меню"""
    await message.answer(
        "🏠 Главное меню",
        reply_markup=get_main_menu_keyboard()
    )


# Обработчик для кнопок главного меню
@router.message(F.text)
async def handle_main_menu_buttons(message: Message):
    i18n = get_localization()
    text = message.text
    
    # Получаем тексты кнопок из локализации
    analyze_text = i18n.get_button_text('analyze_food')
    profile_text = i18n.get_button_text('profile')
    history_text = i18n.get_button_text('history')
    help_text = i18n.get_button_text('help')
    menu_text = i18n.get_button_text('menu')
    
    if text == analyze_text:
        from app.keyboards.analysis_menu import get_analysis_menu_keyboard
        await message.answer(i18n.get_text('send_photo_for_analysis'), reply_markup=get_analysis_menu_keyboard())
    elif text == profile_text:
        await cmd_profile(message)
    elif text == history_text:
        await message.answer(i18n.get_text('history_development'), reply_markup=get_main_menu_keyboard())
    elif text == help_text:
        await message.answer(
            i18n.get_text('help_text'),
            reply_markup=get_main_menu_keyboard()
        )
    elif text == menu_text:
        await cmd_menu(message)
    # else: не обрабатываем - пропускаем к другим обработчикам

@router.message(Command("profile"))
async def cmd_profile(message: Message):
    i18n = get_localization()
    user_id = message.from_user.id
    
    # Временно создаем user_service
    from app.database import Database
    import os
    database = Database(os.getenv('DATABASE_URL'))  # ← Берем из переменных окружения
    user_service = UserService(database)
    
    user = await user_service.get_user(user_id)
    
    if not user:
        await message.answer("Пользователь не найден")
        return
    
    # Определяем тип подписки
    is_premium = user.subscription_type == "premium"
    daily_limit = 10 if is_premium else 3
    remaining = daily_limit - user.daily_photos_used
    
    # Формируем текст профиля
    profile_text = f"""
{i18n.get_text('profile_title')}

{i18n.get_text('profile_id', user_id=user_id)}
{i18n.get_text('profile_subscription_premium') if is_premium else i18n.get_text('profile_subscription_free')}
{i18n.get_text('profile_used_today', used=user.daily_photos_used, limit=daily_limit)}
{i18n.get_text('profile_remaining', remaining=remaining)}

{i18n.get_text('your_features_title') if is_premium else i18n.get_text('premium_features_title')}
{i18n.get_text('premium_features_list')}
"""
    
    # Используем клавиатуру из отдельного файла
    keyboard = get_profile_keyboard(is_premium=is_premium)
    
    await message.answer(profile_text, reply_markup=keyboard)

# Обработчики callback-запросов для профиля
@router.callback_query(F.data == "refresh_profile")
async def refresh_profile(callback: CallbackQuery):
    await cmd_profile(callback.message)
    await callback.answer("✅ Профиль обновлен")

@router.callback_query(F.data == "premium_menu")
async def show_premium_menu(callback: CallbackQuery):
    i18n = get_localization()
    keyboard = get_premium_menu_keyboard()
    
    await callback.message.edit_text(
        i18n.get_text('subscription_menu_title'),
        reply_markup=keyboard
    )
    await callback.answer()