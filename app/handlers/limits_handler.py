# app/handlers/limits_handler.py
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from app.services.user_service import UserService
from app.core.i18n import get_text

router = Router()

@router.message(Command("limits"))
async def cmd_limits(message: Message, user_service: UserService):
    user_id = message.from_user.id
    limits_info = await user_service.get_user_limits_info(user_id)
    
    status = get_text(user_id, 'premium_active' if limits_info['is_premium'] else 'free_tier')
    
    text = get_text(user_id, 'limits_info').format(
        photos_used=limits_info['photos_used'],
        photos_limit=limits_info['photos_limit'],
        texts_used=limits_info['texts_used'],
        texts_limit=limits_info['texts_limit'],
        status=status
    )
    
    await message.answer(text)