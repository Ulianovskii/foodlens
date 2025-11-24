from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.core.i18n import get_localization

def get_admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для админ-панели"""
    i18n = get_localization()
    
    keyboard = [
        [InlineKeyboardButton(text=i18n.get_text('admin_sub_toggle_free'), callback_data="admin_set_free")],
        [InlineKeyboardButton(text=i18n.get_text('admin_sub_toggle_premium'), callback_data="admin_set_premium")],
        [InlineKeyboardButton(text=i18n.get_text('admin_reset_limits'), callback_data="admin_reset_limits")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)