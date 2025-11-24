# app/middlewares/state_middleware.py
from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
from app.services.session_service import session_service
from app.utils.debug import debug_state

class StateValidationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        
        # Пропускаем команды
        if event.text and event.text.startswith('/'):
            await debug_state(user_id, "MIDDLEWARE", f"Command: {event.text} - passing through")
            return await handler(event, data)
        
        # Если пользователь в сессии анализа и это текст - обрабатываем как уточнение
        if (event.text and 
            session_service.is_user_in_analysis(user_id)):
            
            await debug_state(user_id, "MIDDLEWARE", f"Text in analysis session: '{event.text}' - redirecting to analysis")
            
            # Импортируем здесь чтобы избежать циклических импортов
            from app.handlers.photo_handler import handle_analysis_text
            return await handle_analysis_text(event, data["state"])
        
        # Иначе передаем обычному обработчику
        await debug_state(user_id, "MIDDLEWARE", f"Normal text: '{event.text}' - passing to handler")
        return await handler(event, data)