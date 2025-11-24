from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.core.i18n import get_localization

def get_profile_keyboard(is_premium: bool = False) -> InlineKeyboardMarkup:
    """Inline-клавиатура для профиля"""
    i18n = get_localization()
    
    if not is_premium:
        keyboard = [
            [InlineKeyboardButton(text=i18n.get_text('btn_get_premium'), callback_data="premium_menu")],
            [InlineKeyboardButton(text=i18n.get_text('btn_refresh_profile'), callback_data="refresh_profile")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton(text=i18n.get_text('btn_refresh_profile'), callback_data="refresh_profile")]
        ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_premium_menu_keyboard() -> InlineKeyboardMarkup:
    """Inline-клавиатура для меню премиум-подписки"""
    i18n = get_localization()
    
    keyboard = [
        [InlineKeyboardButton(text=i18n.get_text('subscription_week', price="50"), callback_data="subscribe_week")],
        [InlineKeyboardButton(text=i18n.get_text('subscription_month', price="150"), callback_data="subscribe_month")],
        [InlineKeyboardButton(text=i18n.get_text('btn_enter_promo'), callback_data="enter_promo")],
        [InlineKeyboardButton(text=i18n.get_text('btn_back_to_profile'), callback_data="refresh_profile")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)