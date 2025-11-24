#app/keyboards/promo_keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.core.i18n import get_localization

def get_premium_menu_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для меню премиум подписки"""
    i18n = get_localization()
    
    keyboard = [
        [InlineKeyboardButton(text=i18n.get_text('subscription_week', price="50"), callback_data="subscribe_week")],
        [InlineKeyboardButton(text=i18n.get_text('subscription_month', price="150"), callback_data="subscribe_month")],
        [InlineKeyboardButton(text=i18n.get_text('btn_enter_promo'), callback_data="enter_promo")],
        [InlineKeyboardButton(text=i18n.get_text('btn_back_to_profile'), callback_data="refresh_profile")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_promo_enter_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для ввода промокода"""
    i18n = get_localization()
    
    keyboard = [
        [InlineKeyboardButton(text=i18n.get_text('cancel'), callback_data="refresh_profile")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)