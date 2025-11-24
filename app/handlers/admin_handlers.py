from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from app.services.user_service import UserService
from app.services.promo_service import PromoService
from app.services.limit_service import LimitService
from app.core.i18n import get_localization
import os

# Получаем ID админов из .env
ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_USER_IDS', '').split(',') if id.strip()]

admin_router = Router()

def admin_required(handler):
    """Декоратор для проверки прав администратора"""
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id not in ADMIN_IDS:
            await message.answer("⛔️ Команда доступна только администраторам")
            return
        return await handler(message, *args, **kwargs)
    return wrapper

@admin_router.message(Command("generate_promo"))
@admin_required
async def cmd_generate_promo(message: Message, promo_service: PromoService):
    """Генерация промокода: /generate_promo week 1"""
    try:
        parts = message.text.split()
        if len(parts) != 3:
            await message.answer("❌ Использование: /generate_promo <week|month> <количество>")
            return
        
        promo_type = parts[1]
        count = int(parts[2])
        
        if promo_type not in ['week', 'month']:
            await message.answer("❌ Тип промокода должен быть 'week' или 'month'")
            return
        
        # Генерируем промокоды
        promo_codes = await promo_service.create_promo_codes(
            promo_type=f"premium_{promo_type}", 
            count=count, 
            days_valid=30
        )
        
        response = f"🎁 Сгенерировано промокодов ({promo_type}):\n\n"
        for code in promo_codes:
            response += f"`{code}`\n"
        
        await message.answer(response)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@admin_router.message(Command("reset_limits"))
@admin_required
async def cmd_reset_limits(message: Message, limit_service: LimitService, user_service: UserService):
    """Сброс лимитов пользователя: /reset_limits [user_id]"""
    try:
        parts = message.text.split()
        user_id = int(parts[1]) if len(parts) > 1 else message.from_user.id
        
        success = await limit_service.reset_user_limits(user_id)
        if success:
            await message.answer(f"✅ Лимиты пользователя {user_id} сброшены")
        else:
            await message.answer("❌ Ошибка сброса лимитов")
            
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@admin_router.message(Command("reset_sub"))
@admin_required
async def cmd_reset_subscription(message: Message, user_service: UserService):
    """Сброс подписки пользователя: /reset_sub [user_id]"""
    try:
        parts = message.text.split()
        user_id = int(parts[1]) if len(parts) > 1 else message.from_user.id
        
        success = await user_service.downgrade_to_free(user_id)
        if success:
            await message.answer(f"✅ Подписка пользователя {user_id} сброшена")
        else:
            await message.answer("❌ Ошибка сброса подписки")
            
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@admin_router.message(Command("user_info"))
@admin_required
async def cmd_user_info(message: Message, user_service: UserService):
    """Информация о пользователе: /user_info [user_id]"""
    try:
        parts = message.text.split()
        user_id = int(parts[1]) if len(parts) > 1 else message.from_user.id
        
        user_data = await user_service.get_user(user_id)
        if not user_data:
            await message.answer("❌ Пользователь не найден")
            return
        
        from app.models.user import User
        user = User.from_dict(user_data)
        
        subscription_info = "нет"
        if user.subscription_until:
            subscription_info = f"{user.subscription_type} до {user.subscription_until.strftime('%d.%m.%Y')}"
        
        info = f"""
👤 Информация о пользователе:
ID: {user.user_id}
Username: @{user.username or 'нет'}
Имя: {user.first_name or 'не указано'}
Подписка: {subscription_info}
Фото сегодня: {user.daily_photos_used}/{user.get_daily_limit()}
Всего фото: {user.total_photos_analyzed}
Лимит обновляется: {user.last_reset_date.strftime('%d.%m.%Y')}
        """
        
        await message.answer(info)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@admin_router.message(Command("promo_list"))
@admin_required
async def cmd_promo_list(message: Message, promo_service: PromoService):
    """Список активных промокодов"""
    try:
        promos = await promo_service.get_all_promo_codes()
        
        if not promos:
            await message.answer("📭 Нет промокодов")
            return
        
        response = "🎁 Все промокоды:\n\n"
        for promo in promos:
            status = "✅ активен" if promo.is_valid() else "❌ использован/просрочен"
            response += f"`{promo.code}` - {promo.promo_type} ({status})\n"
        
        await message.answer(response)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@admin_router.message(Command("activate_promo"))
@admin_required  
async def cmd_activate_promo(message: Message, promo_service: PromoService, user_service: UserService):
    """Активировать промокод для пользователя: /activate_promo CODE [user_id]"""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Использование: /activate_promo <код> [user_id]")
            return
        
        code = parts[1]
        user_id = int(parts[2]) if len(parts) > 2 else message.from_user.id
        
        user_data = await user_service.get_user(user_id)
        if not user_data:
            await message.answer("❌ Пользователь не найден")
            return
        
        from app.models.user import User
        user = User.from_dict(user_data)
        
        success = await promo_service.activate_promo_code(code, user)
        if success:
            await message.answer(f"✅ Промокод {code} активирован для пользователя {user_id}")
        else:
            await message.answer("❌ Неверный или уже использованный промокод")
            
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")