from .basic_commands import router as basic_router
from .photo_handler import food_photo_router as photo_router
from .admin_handlers import router as admin_router

# Экспортируем все роутеры
__all__ = ['basic_router', 'photo_router', 'admin_router', 'router']

# Объединяем все роутеры в один главный
router = basic_router
router.include_router(photo_router)
router.include_router(admin_router)  # ← ДОБАВИТЬ ЭТУ СТРОКУ