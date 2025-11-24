# app/middlewares/limit_middleware.py
from aiogram import BaseMiddleware
from aiogram.types import Message
from app.services.user_service import UserService

class LimitMiddleware(BaseMiddleware):
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            # Проверяем лимиты только для фото и текстовых сообщений в состоянии анализа
            if event.photo:
                user_id = event.from_user.id
                if not await self.user_service.increment_photo_counter(user_id):
                    # Лимит исчерпан
                    from app.core.i18n import get_text
                    text = get_text(user_id, 'limit_exceeded')
                    await event.answer(text)
                    return
            
            # Для текстовых сообщений в контексте анализа
            elif event.text and event.text not in ['/start', '/help', '/cancel']:
                # Здесь нужно проверить находится ли пользователь в состоянии анализа
                # Пока пропускаем, добавим когда будет FSM
                pass
        
        return await handler(event, data)