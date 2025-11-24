# app/handlers/__init__.py
from .admin_handlers import admin_router
from .basic_commands import router as basic_router
from .photo_handler import router as photo_router
from .promo_handlers import router as promo_router

# Объединяем все роутеры в один главный роутер
router = admin_router
router.include_router(basic_router)
router.include_router(photo_router)
router.include_router(promo_router)