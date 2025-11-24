# app/handlers/basic_commands.py - ИСПРАВЛЕННЫЙ
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from app.core.i18n import get_localization

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
        await message.answer(i18n.get_text('profile_development'))
    elif text == i18n.get_button_text('history'):
        await message.answer(i18n.get_text('history_development'))
    elif text == i18n.get_button_text('help'):
        await message.answer(
            i18n.get_text('help_text'),
            reply_markup=get_main_keyboard()
        )