from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from app.locales import get_text

# Создаем роутер для базовых команд
basic_router = Router()


@basic_router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Обработчик команды /start
    """
    text = get_text('start_welcome')
    await message.answer(text)


@basic_router.message(Command("help"))
async def cmd_help(message: Message):
    """
    Обработчик команды /help
    """
    text = get_text('help_text')
    await message.answer(text)


@basic_router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """
    Обработчик команды /cancel - отмена текущего состояния
    """
    current_state = await state.get_state()
    if current_state is None:
        text = get_text('cancel_no_action')
        await message.answer(text)
        return

    await state.clear()
    text = get_text('cancel_success')
    await message.answer(text)


@basic_router.message(Command("history"))
async def cmd_history(message: Message):
    """
    Обработчик команды /history (заглушка)
    """
    text = get_text('history_development')
    await message.answer(text)


@basic_router.message(Command("analyze"))
async def cmd_analyze(message: Message):
    """
    Обработчик команды /analyze
    """
    text = get_text('analyze_instructions')
    await message.answer(text)


@basic_router.message(Command("profile"))
async def cmd_profile(message: Message):
    """
    Обработчик команды /profile (заглушка)
    """
    text = get_text('profile_development')
    await message.answer(text)


# Обработчик для любых текстовых сообщений, не являющихся командами
@basic_router.message(F.text)
async def handle_other_text(message: Message):
    """
    Обработчик любых текстовых сообщений, не являющихся командами
    """
    text = get_text('unknown_text')
    await message.answer(text)