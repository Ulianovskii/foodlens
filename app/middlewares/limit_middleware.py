from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable

from app.services.limit_service import LimitService


class LimitMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Проверяем только сообщения с фото
        if not isinstance(event, Message) or not event.photo:
            return await handler(event, data)
        
        database = data['database']
        user = data['user']
        locale = data['locale']
        
        limit_service = LimitService(database)
        
        # Проверяем и увеличиваем счетчик
        if not await limit_service.check_and_increment_usage(user):
            # Лимит исчерпан
            remaining = user.get_remaining_photos()
            text = locale.get_text("limit_exceeded_detailed").format(
                used=user.daily_photos_used,
                limit=user.get_daily_limit(),
                remaining=remaining
            )
            
            # Добавляем рекламу для бесплатных пользователей
            if not user.has_premium():
                text += "\n\n" + locale.get_text("premium_ad")
            
            await event.answer(text)
            return
        
        # Лимит не исчерпан, продолжаем обработку
        return await handler(event, data)