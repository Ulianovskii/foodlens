# app/handlers/basic_commands.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from app.core.i18n import get_localization
from app.keyboards.main_menu import get_main_menu_keyboard

basic_router = Router()

@basic_router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    i18n = get_localization()
    await message.answer(
        i18n.get_text("start_welcome"),
        reply_markup=get_main_menu_keyboard()
    )

@basic_router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    i18n = get_localization()
    await message.answer(i18n.get_text("help_text"))

@basic_router.message(Command("cancel"))
async def cmd_cancel(message: Message):
    """Обработчик команды /cancel"""
    i18n = get_localization()
    await message.answer(
        i18n.get_text("cancel_no_action"),
        reply_markup=get_main_menu_keyboard()
    )

@basic_router.message(Command("history"))
async def cmd_history(message: Message):
    """Обработчик команды /history"""
    i18n = get_localization()
    await message.answer(i18n.get_text("history_development"))

# Добавляем обработчики для кнопок главного меню
@basic_router.message(F.text == "❓ Помощь")
async def button_help(message: Message):
    """Обработчик кнопки помощи"""
    i18n = get_localization()
    await message.answer(i18n.get_text("help_text"))

@basic_router.message(F.text == "📊 Журнал")
async def button_history(message: Message):
    """Обработчик кнопки журнала"""
    i18n = get_localization()
    await message.answer(i18n.get_text("history_development"))

@basic_router.message(F.text == "👤 Профиль")
async def button_profile(message: Message):
    """Обработчик кнопки профиля"""
    i18n = get_localization()
    await message.answer(i18n.get_text("profile_development"))