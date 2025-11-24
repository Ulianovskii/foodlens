# app/keyboards/analysis_menu.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from app.core.i18n import get_localization

def get_analysis_menu_keyboard():
    """Клавиатура после загрузки фото"""
    i18n = get_localization()
    builder = ReplyKeyboardBuilder()
    
    builder.add(
        KeyboardButton(text=i18n.get_button_text("nutrition")),
        KeyboardButton(text=i18n.get_button_text("recipe")),
        KeyboardButton(text=i18n.get_button_text("new_photo")),
        KeyboardButton(text=i18n.get_button_text("menu"))  # ← ИСПОЛЬЗУЕМ ЛОКАЛИЗАЦИЮ
    )
    
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)