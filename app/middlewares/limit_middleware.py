from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
from app.services.user_service import UserService
from app.services.limit_service import LimitService
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

        # Получаем user_service из data
        user_service: UserService = data.get('user_service')
        if not user_service:
            return await handler(event, data)

        try:
            user_id = event.from_user.id
            
            # Получаем или создаем пользователя
            user_data = await user_service.get_or_create_user(user_id)
            
            # Создаем объект User из данных
            from app.models.user import User
            user = User.from_dict(user_data)
            
            # Создаем limit_service и проверяем лимиты
            limit_service = LimitService(user_service.database)
            can_proceed = await limit_service.check_and_increment_usage(user)
            
            if not can_proceed:
                i18n = get_localization()
                await event.answer(i18n.get_text('daily_limit_exceeded'))
                return
            
            return await handler(event, data)
            
        except Exception as e:
            logger.error(f"Ошибка в middleware: {e}")
            return await handler(event, data)