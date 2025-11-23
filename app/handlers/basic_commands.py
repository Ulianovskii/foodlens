# app/handlers/basic_commands.py
from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from app.core.i18n import get_localization
from app.keyboards.main_menu import get_main_menu_keyboard

# Создаем роутер для базовых команд
basic_router = Router()

@basic_router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Обработчик команды /start
    """
    i18n = get_localization()
    text = i18n.get_text('start_welcome')
    await message.answer(
        text,
        reply_markup=get_main_menu_keyboard()
    )

@basic_router.message(Command("help"))
async def cmd_help(message: Message):
    """
    Обработчик команды /help
    """
    i18n = get_localization()
    text = i18n.get_text('help_text')
    await message.answer(text)

@basic_router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """
    Обработчик команды /cancel - отмена текущего состояния
    """
    i18n = get_localization()
    current_state = await state.get_state()
    if current_state is None:
        text = i18n.get_text('cancel_no_action')
        await message.answer(text)
        return

    await state.clear()
    text = i18n.get_text('cancel_success')
    await message.answer(
        text,
        reply_markup=get_main_menu_keyboard()
    )

@basic_router.message(Command("history"))
async def cmd_history(message: Message):
    """
    Обработчик команды /history (заглушка)
    """
    i18n = get_localization()
    text = i18n.get_text('history_development')
    await message.answer(text)

@basic_router.message(Command("profile"))
async def cmd_profile(message: Message):
    """
    Обработчик команды /profile (заглушка)
    """
    i18n = get_localization()
    text = i18n.get_text('profile_development')
    await message.answer(text)

# Обработчик для любых текстовых сообщений, не являющихся командами
# ТОЛЬКО когда нет активного состояния
@basic_router.message(F.text, StateFilter(None))
async def handle_other_text(message: Message):
    """
    Обработчик любых текстовых сообщений, не являющихся командами
    """
    i18n = get_localization()
    text = i18n.get_text('unknown_text')
    await message.answer(
        text,
        reply_markup=get_main_menu_keyboard()
    )