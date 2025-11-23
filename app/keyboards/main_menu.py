# app/keyboards/main_menu.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from app.core.i18n import get_localization

def get_main_menu_keyboard():
    """Клавиатура основного меню"""
    i18n = get_localization()
    builder = ReplyKeyboardBuilder()
    
    builder.add(
        KeyboardButton(text=i18n.get_button_text("analyze_food")),
        KeyboardButton(text=i18n.get_button_text("profile")),
        KeyboardButton(text=i18n.get_button_text("help")),
        KeyboardButton(text=i18n.get_button_text("history"))
    )
    
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)