from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
from app.services.user_service import UserService
from app.core.i18n import get_localization
import logging

logger = logging.getLogger(__name__)


class LimitMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Пропускаем все сообщения без фото
        if not event.photo:
            return await handler(event, data)

        try:
            # Получаем user_service из бота (а не из data)
            user_service = getattr(event.bot, 'user_service', None)
            if not user_service:
                logger.error("user_service не найден в боте")
                return await handler(event, data)

            user_id = event.from_user.id
            
            # Получаем пользователя (используем get_user вместо get_or_create_user)
            user = await user_service.get_user(user_id)
            if not user:
                # Если пользователя нет, создаем его через save_user
                from app.models.user import User
                from datetime import datetime, date
                user = User(
                    user_id=user_id,
                    username=event.from_user.username,
                    created_at=datetime.now(),
                    last_reset_date=date.today()
                )
                await user_service.save_user(user)
            
            # Проверяем может ли пользователь анализировать фото
            if not user.can_analyze_photo():
                i18n = get_localization()
                await event.answer(i18n.get_text('daily_limit_exceeded'))
                return
            
            # Увеличиваем счетчик фото
            success = await user_service.increment_photo_counter(user)
            if not success:
                i18n = get_localization()
                await event.answer(i18n.get_text('daily_limit_exceeded'))
                return
            
            return await handler(event, data)
            
        except Exception as e:
            logger.error(f"Ошибка в middleware: {e}")
            return await handler(event, data)