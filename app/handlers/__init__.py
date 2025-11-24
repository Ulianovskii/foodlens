from .basic_commands import router as basic_router
from .photo_handler import router as photo_router
from .limits_handler import router as limits_router

# Объединяем все роутеры
router = basic_router
router.include_router(photo_router)
router.include_router(limits_router)