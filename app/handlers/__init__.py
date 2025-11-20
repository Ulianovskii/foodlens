from aiogram import Router

from .basic_commands import basic_router
from .photo_handler import photo_router

router = Router()
router.include_router(basic_router)
router.include_router(photo_router)

__all__ = ["router"]