# app/handlers/basic_commands.py - ИСПРАВЛЕННЫЙ
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from app.core.i18n import get_localization
from app.services.user_service import UserService

router = Router()

def get_main_keyboard():
    """Возвращает основную клавиатуру"""
    i18n = get_localization()
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=i18n.get_button_text('analyze_food')),
                KeyboardButton(text=i18n.get_button_text('profile'))
            ],
            [
                KeyboardButton(text=i18n.get_button_text('history')),
                KeyboardButton(text=i18n.get_button_text('help'))
            ]
        ],
        resize_keyboard=True
    )

@router.message(Command("start"))
async def cmd_start(message: Message):
    i18n = get_localization()
    
    await message.answer(
        f"{i18n.get_text('start_welcome')}\n\n",
        reply_markup=get_main_keyboard()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    i18n = get_localization()
    await message.answer(
        i18n.get_text('help_text'),
        reply_markup=get_main_keyboard()
    )

@router.message(Command("cancel"))
async def cmd_cancel(message: Message):
    i18n = get_localization()
    await message.answer(
        i18n.get_text('cancel_success'),
        reply_markup=get_main_keyboard()
    )

@router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Команда для возврата в главное меню"""
    await message.answer(
        "🏠 Главное меню",
        reply_markup=get_main_keyboard()
    )

# Обработчик для кнопок главного меню
@router.message(F.text.in_([
    "📸 Анализировать еду", 
    "👤 Профиль", 
    "📊 Журнал", 
    "❓ Помощь"
]))
async def handle_main_menu_buttons(message: Message):
    i18n = get_localization()
    text = message.text
    
    if text == i18n.get_button_text('analyze_food'):
        await message.answer(i18n.get_text('send_photo_for_analysis'))
    elif text == i18n.get_button_text('profile'):
        # Вместо заглушки вызываем команду профиля
        await cmd_profile(message)
    elif text == i18n.get_button_text('history'):
        await message.answer(i18n.get_text('history_development'))
    elif text == i18n.get_button_text('help'):
        await message.answer(
            i18n.get_text('help_text'),
            reply_markup=get_main_keyboard()
        )

@router.message(Command("profile"))
async def cmd_profile(message: Message):
    i18n = get_localization()
    user_id = message.from_user.id
    user = await UserService.get_user(user_id)
    
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
    
    # Клавиатура
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=i18n.get_text('btn_get_premium'), callback_data="premium_menu")],
        [InlineKeyboardButton(text=i18n.get_text('btn_refresh_profile'), callback_data="refresh_profile")]
    ]) if not is_premium else InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=i18n.get_text('btn_refresh_profile'), callback_data="refresh_profile")]
    ])
    
    await message.answer(profile_text, reply_markup=keyboard)

# Обработчики callback-запросов для профиля
@router.callback_query(F.data == "refresh_profile")
async def refresh_profile(callback: CallbackQuery):
    await cmd_profile(callback.message)
    await callback.answer("✅ Профиль обновлен")

@router.callback_query(F.data == "premium_menu")
async def show_premium_menu(callback: CallbackQuery):
    i18n = get_localization()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=i18n.get_text('subscription_week', price="50"), callback_data="subscribe_week")],
        [InlineKeyboardButton(text=i18n.get_text('subscription_month', price="150"), callback_data="subscribe_month")],
        [InlineKeyboardButton(text=i18n.get_text('btn_enter_promo'), callback_data="enter_promo")],
        [InlineKeyboardButton(text=i18n.get_text('btn_back_to_profile'), callback_data="refresh_profile")]
    ])
    
    await callback.message.edit_text(
        i18n.get_text('subscription_menu_title'),
        reply_markup=keyboard
    )
    await callback.answer()