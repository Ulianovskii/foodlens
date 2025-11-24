# app/utils/debug.py
import logging
from aiogram import types
from datetime import datetime

logger = logging.getLogger(__name__)

async def debug_state(user_id: int, handler: str, message: str = ""):
    """Логирование состояний для отладки"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    debug_msg = f"[{timestamp}] USER:{user_id} HANDLER:{handler} | {message}"
    logger.debug(debug_msg)
    print(f"🔍 {debug_msg}")

async def log_message_flow(message: types.Message, context: str):
    """Логирование потока сообщений"""
    user_id = message.from_user.id
    text = message.text or message.caption or "[media]"
    await debug_state(user_id, "MESSAGE_FLOW", f"{context}: '{text}'")