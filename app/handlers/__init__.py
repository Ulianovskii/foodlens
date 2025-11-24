from .basic_commands import router as basic_router
from .photo_handler import food_photo_router as photo_router
from .admin_handlers import admin_router  # ← ИСПРАВИТЬ!

# Объединяем все роутеры
router = basic_router
router.include_router(photo_router)
router.include_router(admin_router)  # ← ДОБАВИТЬ!