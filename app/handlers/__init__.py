# app/handlers/__init__.py
from aiogram import Router

from .basic_commands import router as basic_router
from .photo_handler import router as photo_router
from .promo_handlers import router as promo_router
from .admin_handlers import router as admin_router

router = Router()

# Важно: более специфичные роутеры регистрируем первыми
router.include_router(promo_router)  # Промокоды - высокий приоритет
router.include_router(admin_router)  # Админка
router.include_router(photo_router)  # Фото обработка
router.include_router(basic_router)  # Базовые команды - низкий приоритет