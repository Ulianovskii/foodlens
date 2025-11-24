#app/handlers/__init__.py
from aiogram import Router

from .promo_handlers import router as promo_router    # ← ПЕРВЫЙ
from .admin_handlers import router as admin_router
from .photo_handler import router as photo_router  
from .basic_commands import router as basic_router    # ← ПОСЛЕДНИЙ

router = Router()

# Промокоды ДОЛЬШНЫ БЫТЬ ПЕРВЫМИ
router.include_router(promo_router)
router.include_router(admin_router)
router.include_router(photo_router)
router.include_router(basic_router)

__all__ = ['router']