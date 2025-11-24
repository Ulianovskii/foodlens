# app/handlers/__init__.py
from .basic_commands import router as basic_router
from .photo_handler import food_photo_router as photo_router

# Объединяем все роутеры
router = basic_router
router.include_router(photo_router)
