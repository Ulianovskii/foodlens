# app/handlers/__init__.py
from .basic_commands import basic_router
from .photo_handler import food_photo_router  # ИЗМЕНИЛИ

# Объединяем все роутеры
router = basic_router
router.include_router(food_photo_router)  # ИЗМЕНИЛИ