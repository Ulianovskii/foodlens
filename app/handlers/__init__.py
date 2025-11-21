from .photo_handler import router as photo_router
from .base_handler import router as base_router

# Объединяем все роутеры
router = base_router
router.include_router(photo_router)