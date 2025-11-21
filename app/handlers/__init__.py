# app/handlers/__init__.py
from .photo_handler import photo_router
from .basic_commands import router as basic_router

# Объединяем все роутеры
router = base_router
router.include_router(photo_router)