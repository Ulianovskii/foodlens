# app/handlers/admin_handlers.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app.services.user_service import UserService
from app.services.promo_service import PromoService
from app.core.i18n import get_localization
from app.keyboards.admin_keyboards import get_admin_panel_keyboard
import os
import logging

logger = logging.getLogger(__name__)

# Получаем ID админов из .env
ADMIN_IDS_STR = os.getenv('ADMIN_USER_IDS', '')
ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(',') if id.strip()]

# ДОБАВЬ ЭТОТ ОТЛАДОЧНЫЙ ВЫВОД
logger.info(f"🔧 Загружены ADMIN_IDS: {ADMIN_IDS} из строки: '{ADMIN_IDS_STR}'")

admin_router = Router()

def admin_required(handler):
    """Декоратор для проверки прав администратора для Message"""
    async def wrapper(message: Message, *args, **kwargs):
        user_id = message.from_user.id
        logger.info(f"🔧 Проверка прав админа для пользователя {user_id}, ADMIN_IDS: {ADMIN_IDS}")
        
        if user_id not in ADMIN_IDS:
            logger.warning(f"⛔️ Отказано в доступе пользователю {user_id}")
            i18n = get_localization()
            await message.answer(i18n.get_text('admin_access_denied'))
            return
        logger.info(f"✅ Доступ разрешен пользователю {user_id}")
        return await handler(message, *args, **kwargs)
    return wrapper

def admin_callback_required(handler):
    """Декоратор для проверки прав администратора для CallbackQuery"""
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        user_id = callback.from_user.id
        if user_id not in ADMIN_IDS:
            logger.warning(f"⛔️ Отказано в доступе пользователю {user_id} для callback")
            i18n = get_localization()
            await callback.answer(i18n.get_text('admin_access_denied'), show_alert=True)
            return
        return await handler(callback, *args, **kwargs)
    return wrapper

# ===== ТЕКСТОВЫЕ КОМАНДЫ =====

@admin_router.message(Command("generate_promo"))
@admin_required
async def cmd_generate_promo(message: Message):
    """Генерация промокода: /generate_promo week 1"""
    try:
        i18n = get_localization()
        parts = message.text.split()
        if len(parts) != 3:
            await message.answer(i18n.get_text('admin_generate_promo_usage'))
            return
        
        promo_type = parts[1]
        count = int(parts[2])
        
        if promo_type not in ['week', 'month']:
            await message.answer(i18n.get_text('admin_invalid_promo_type'))
            return
        
        # Получаем сервисы из контекста бота
        promo_service = PromoService(message.bot.user_service.database)
        
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
async def cmd_reset_limits(message: Message):
    """Сброс лимитов пользователя: /reset_limits [user_id]"""
    try:
        i18n = get_localization()
        parts = message.text.split()
        user_id = int(parts[1]) if len(parts) > 1 else message.from_user.id
        
        user_service = UserService(message.bot.user_service.database)
        user = await user_service.get_user(user_id)
        
        if user:
            await user_service.reset_daily_limits(user_id)
            await message.answer(i18n.get_text('admin_limits_reset', user_id=user_id))
        else:
            await message.answer(i18n.get_text('admin_user_not_found'))
            
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@admin_router.message(Command("reset_sub"))
@admin_required
async def cmd_reset_subscription(message: Message):
    """Сброс подписки пользователя: /reset_sub [user_id]"""
    try:
        i18n = get_localization()
        parts = message.text.split()
        user_id = int(parts[1]) if len(parts) > 1 else message.from_user.id
        
        user_service = UserService(message.bot.user_service.database)
        await user_service.update_subscription(user_id, "free")
        await message.answer(i18n.get_text('admin_subscription_reset', user_id=user_id))
            
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@admin_router.message(Command("user_info"))
@admin_required
async def cmd_user_info(message: Message):
    """Информация о пользователе: /user_info [user_id]"""
    try:
        parts = message.text.split()
        user_id = int(parts[1]) if len(parts) > 1 else message.from_user.id
        
        user_service = UserService(message.bot.user_service.database)
        user = await user_service.get_user(user_id)
        
        if not user:
            i18n = get_localization()
            await message.answer(i18n.get_text('admin_user_not_found'))
            return
        
        subscription_info = "нет"
        if user.subscription_until:
            subscription_info = f"{user.subscription_type} до {user.subscription_until.strftime('%d.%m.%Y')}"
        
        info = f"""
👤 Информация о пользователе:
ID: {user.user_id}
Username: @{user.username or 'нет'}
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
async def cmd_promo_list(message: Message):
    """Список активных промокодов"""
    try:
        i18n = get_localization()
        promo_service = PromoService(message.bot.user_service.database)
        promos = await promo_service.get_all_promo_codes()
        
        if not promos:
            await message.answer(i18n.get_text('admin_no_promos'))
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
async def cmd_activate_promo(message: Message):
    """Активировать промокод для пользователя: /activate_promo CODE [user_id]"""
    try:
        i18n = get_localization()
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer(i18n.get_text('admin_activate_promo_usage'))
            return
        
        code = parts[1]
        user_id = int(parts[2]) if len(parts) > 2 else message.from_user.id
        
        user_service = UserService(message.bot.user_service.database)
        user = await user_service.get_user(user_id)
        
        if not user:
            await message.answer(i18n.get_text('admin_user_not_found'))
            return
        
        promo_service = PromoService(message.bot.user_service.database)
        success = await promo_service.activate_promo_code(code, user)
        
        if success:
            await message.answer(i18n.get_text('admin_promo_activated', code=code, user_id=user_id))
        else:
            await message.answer(i18n.get_text('admin_invalid_promo'))
            
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

# ===== ИНТЕРАКТИВНАЯ АДМИН-ПАНЕЛЬ =====

@admin_router.message(Command("superadmin"))
@admin_required
async def admin_panel(message: Message):
    """Интерактивная админ-панель"""
    i18n = get_localization()
    
    await message.answer(
        "🛠️ Админ-панель\n\nВыберите действие:", 
        reply_markup=get_admin_panel_keyboard()
    )

@admin_router.callback_query(F.data.startswith("admin_"))
@admin_callback_required
async def admin_actions(callback: CallbackQuery):
    """Обработка действий из админ-панели"""
    i18n = get_localization()
    user_id = callback.from_user.id
    action = callback.data
    
    user_service = UserService(callback.bot.user_service.database)
    
    if action == "admin_set_free":
        await user_service.update_subscription(user_id, "free")
        await callback.answer("✅ Установлен бесплатный тариф")
    
    elif action == "admin_set_premium":
        from datetime import datetime, timedelta
        subscription_until = datetime.now() + timedelta(days=30)
        await user_service.update_subscription(user_id, "premium_month", subscription_until)
        await callback.answer("✅ Установлен премиум тариф на 30 дней")
    
    elif action == "admin_reset_limits":
        await user_service.reset_daily_limits(user_id)
        await callback.answer("✅ Лимиты сброшены")
    
    # Обновляем сообщение с кнопками
    await callback.message.edit_reply_markup(reply_markup=get_admin_panel_keyboard())