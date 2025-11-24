#app/keyboards/inline_menus.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.core.i18n import get_localization

def get_profile_keyboard(is_premium: bool = False) -> InlineKeyboardMarkup:
    """Inline-клавиатура для профиля"""
    i18n = get_localization()
    
    if not is_premium:
        keyboard = [
            [InlineKeyboardButton(text=i18n.get_text('btn_get_premium'), callback_data="get_premium")],
            [InlineKeyboardButton(text=i18n.get_button_text('menu'), callback_data="main_menu")]  # ← Главная вместо Обновить
        ]
    else:
        keyboard = [
            [InlineKeyboardButton(text=i18n.get_button_text('menu'), callback_data="main_menu")]  # ← Главная
        ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)