from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from app.services.promo_service import PromoService
from app.services.limit_service import LimitService
from app.models.promo import PromoType

router = Router()

# Только для администраторов (замените на ваш telegram_id)
ADMIN_IDS = [123456789]  # ← ЗАМЕНИТЕ НА ВАШ ID

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

@router.message(Command("generate_promos"))
async def generate_promos(message: Message, db):  # ← УБРАТЬ ТИП
    """Генерация промокодов"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        # /generate_promos week 5
        args = message.text.split()[1:]
        promo_type = args[0] if args else "week"
        count = int(args[1]) if len(args) > 1 else 1
        
        promo_service = PromoService(db)
        
        if promo_type == "week":
            promo_codes = await promo_service.create_promo_codes(PromoType.PREMIUM_WEEK.value, count)
        elif promo_type == "month":
            promo_codes = await promo_service.create_promo_codes(PromoType.PREMIUM_MONTH.value, count)
        else:
            await message.answer("❌ Неверный тип промокода. Используйте: week или month")
            return
        
        response = f"✅ Сгенерировано промокодов ({promo_type}):\n\n"
        for code in promo_codes:
            response += f"`{code}`\n"
        
        await message.answer(response, parse_mode="Markdown")
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

@router.message(Command("reset_promos"))
async def reset_promos(message: Message, db):  # ← УБРАТЬ ТИП
    """Сбросить все промокоды"""
    if not is_admin(message.from_user.id):
        return
    
    promo_service = PromoService(db)
    await promo_service.reset_promo_codes()
    await message.answer("✅ Все промокоды сброшены")

@router.message(Command("reset_my_limits"))
async def reset_my_limits(message: Message, db, user):  # ← УБРАТЬ ТИП
    """Сбросить лимиты текущего пользователя"""
    limit_service = LimitService(db)
    await limit_service.reset_my_limits(user)
    await message.answer("✅ Ваши лимиты сброшены")

@router.message(Command("reset_limits"))
async def reset_limits(message: Message, db):  # ← УБРАТЬ ТИП
    """Сбросить лимиты пользователя по telegram_id"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        telegram_id = int(message.text.split()[1])
        limit_service = LimitService(db)
        
        if await limit_service.reset_user_limits(telegram_id):
            await message.answer(f"✅ Лимиты пользователя {telegram_id} сброшены")
        else:
            await message.answer("❌ Пользователь не найден")
            
    except (IndexError, ValueError):
        await message.answer("❌ Использование: /reset_limits <telegram_id>")

@router.message(Command("promo_list"))
async def promo_list(message: Message, db):  # ← УБРАТЬ ТИП
    """Список всех промокодов"""
    if not is_admin(message.from_user.id):
        return
    
    promo_service = PromoService(db)
    promos = await promo_service.get_all_promo_codes()
    
    if not promos:
        await message.answer("📭 Нет активных промокодов")
        return
    
    response = "📋 Список промокодов:\n\n"
    for promo in promos:
        status = "✅ Активен" if promo.is_valid() else "❌ Использован"
        used_by = f" (использовал: {promo.used_by})" if promo.is_used else ""
        response += f"`{promo.code}` - {promo.promo_type} - {status}{used_by}\n"
    
    await message.answer(response, parse_mode="Markdown")