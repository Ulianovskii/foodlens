# app/handlers/basic_commands.py
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from app.services.user_service import UserService
from app.core.i18n import get_localization
from app.keyboards.main_menu import get_main_menu_keyboard
#from app.keyboards.inline_menus import get_profile_keyboard  
from app.keyboards.promo_keyboards import get_premium_menu_keyboard
from datetime import datetime, date  # ← ВЫНЕС ИМПОРТ В НАЧАЛО

router = Router()

async def show_user_profile(message: Message):
    """Функция для показа профиля пользователя (используется в других модулях)"""
    i18n = get_localization()
    user_id = message.from_user.id
    
    # Получаем user_service из бота
    user_service = getattr(message.bot, 'user_service', None)
    
    if not user_service:
        await message.answer("❌ Сервис недоступен")
        return
        
    user = await user_service.get_user(user_id)
    
    if not user:
        # Если пользователя нет - создаем его
        from app.models.user import User
        user = User(
            user_id=user_id,
            username=message.from_user.username,
            created_at=datetime.now(),
            last_reset_date=date.today()
        )
        await user_service.save_user(user)
        # Теперь получаем созданного пользователя
        user = await user_service.get_user(user_id)
    
    # Определяем тип подписки
    is_premium = user.subscription_type != "free" and user.subscription_until and user.subscription_until > datetime.now()
    daily_limit = 10 if is_premium else 3
    remaining = daily_limit - user.daily_photos_used
    
    # Формируем текст профиля с локализацией
    profile_text = f"""
{i18n.get_text('profile_subscription_premium' if is_premium else 'profile_subscription_free')}
{ i18n.get_text('profile_premium_until', date=user.subscription_until.strftime('%d.%m.%Y')) if is_premium and user.subscription_until else ''}
{i18n.get_text('profile_used_today', used=user.daily_photos_used, limit=daily_limit)}
{i18n.get_text('profile_remaining', remaining=remaining)}

{i18n.get_text('your_features_title' if is_premium else 'premium_features_title')}
{i18n.get_text('premium_features_list')}
"""
    
    # Используем клавиатуру из inline_menus.py
    keyboard = get_profile_keyboard(is_premium=is_premium)
    
    await message.answer(profile_text, reply_markup=keyboard)

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


# Обработчики для КОНКРЕТНЫХ кнопок главного меню
@router.message(F.text == get_localization().get_button_text('analyze_food'))
async def handle_analyze_food(message: Message):
    i18n = get_localization()
    from app.keyboards.analysis_menu import get_analysis_menu_keyboard
    await message.answer(i18n.get_text('send_photo_for_analysis'), reply_markup=get_analysis_menu_keyboard())

@router.message(F.text == get_localization().get_button_text('profile'))
async def handle_profile(message: Message):
    await cmd_profile(message)

@router.message(F.text == get_localization().get_button_text('history'))
async def handle_history(message: Message):
    i18n = get_localization()
    await message.answer(i18n.get_text('history_development'), reply_markup=get_main_menu_keyboard())

@router.message(F.text == get_localization().get_button_text('help'))
async def handle_help(message: Message):
    i18n = get_localization()
    await message.answer(i18n.get_text('help_text'), reply_markup=get_main_menu_keyboard())

@router.message(F.text == get_localization().get_button_text('menu'))
async def handle_menu(message: Message):
    await cmd_menu(message)

@router.message(Command("profile"))
async def cmd_profile(message: Message):
    await show_user_profile(message)

# Обработчики callback-запросов для профиля
@router.callback_query(F.data == "refresh_profile")
async def refresh_profile(callback: CallbackQuery):
    await show_user_profile(callback.message)
    await callback.answer("✅ Профиль обновлен")

# Обработчик для кнопки "Получить премиум"
@router.callback_query(F.data == "get_premium")
async def get_premium_handler(callback: CallbackQuery):
    i18n = get_localization()
    await callback.message.answer(
        i18n.get_text('premium_options'),
        reply_markup=get_premium_menu_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "main_menu")
async def main_menu_handler(callback: CallbackQuery):
    """Обработчик возврата в главное меню"""
    await callback.message.answer(
        "🏠 Главное меню",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()