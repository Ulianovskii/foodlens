# app/handlers/promo_handlers.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import logging

from app.services.promo_service import PromoService
from app.services.user_service import UserService
from app.core.i18n import get_localization
from app.keyboards.main_menu import get_main_menu_keyboard

logger = logging.getLogger(__name__)

router = Router()

# Добавляем FSM для промокодов
class PromoStates(StatesGroup):
    waiting_for_promo = State()

@router.callback_query(F.data == "enter_promo")
async def enter_promo(callback: CallbackQuery, state: FSMContext):
    """Обработчик ввода промокода"""
    i18n = get_localization()
    
    # Устанавливаем состояние ожидания промокода
    await state.set_state(PromoStates.waiting_for_promo)
    
    await callback.message.answer(
        i18n.get_text('promo_enter')
    )
    await callback.answer()

@router.message(PromoStates.waiting_for_promo)
async def process_promo_with_state(message: Message, state: FSMContext):
    """Обработка промокода с использованием FSM"""
    i18n = get_localization()
    user_id = message.from_user.id
    
    # Очищаем состояние
    await state.clear()
    
    if not message.text:
        await message.answer("❌ Пожалуйста, введите промокод")
        return
        
    promo_code = message.text.strip().upper()
    
    try:
        # Получаем user_service из бота
        user_service = UserService(message.bot.user_service.database)
        
        # Получаем пользователя
        user = await user_service.get_user(user_id)
        
        if not user:
            await message.answer("❌ Пользователь не найден")
            return
        
        # Активируем промокод
        promo_service = PromoService(user_service.database)
        success, result = await promo_service.activate_promo_code(promo_code, user)
        
        if success:
            # Обновляем данные пользователя
            user = await user_service.get_user(user_id)
            
            # Формируем дату окончания
            until_date = user.subscription_until.strftime("%d.%m.%Y") if user.subscription_until else "неизвестно"
            
            await message.answer(
                i18n.get_text('promo_success', until=until_date),
                reply_markup=get_main_menu_keyboard()
            )
            
        else:
            # Определяем тип ошибки
            error_message = i18n.get_text('promo_invalid')
            if "не найден" in result.lower():
                error_message = i18n.get_text('promo_not_found')
            elif "просрочен" in result.lower():
                error_message = i18n.get_text('promo_expired')
            elif "использован" in result.lower():
                error_message = i18n.get_text('promo_already_used')
            elif "уже есть подписка" in result.lower():
                error_message = i18n.get_text('promo_already_have_subscription')
            
            await message.answer(
                error_message,
                reply_markup=get_main_menu_keyboard()
            )
    
    except Exception as e:
        logger.error(f"Ошибка активации промокода: {e}")
        await message.answer(
            "❌ Произошла ошибка при активации промокода",
            reply_markup=get_main_menu_keyboard()
        )

# Обработчик для отмены ввода промокода
@router.callback_query(F.data == "refresh_profile")
async def cancel_promo(callback: CallbackQuery, state: FSMContext):
    """Отмена ввода промокода и возврат в профиль"""
    # Очищаем состояние
    await state.clear()
    
    # Показываем профиль
    from app.handlers.basic_commands import show_user_profile
    await show_user_profile(callback.message)
    await callback.answer("✅ Возврат в профиль")

# Заглушки для других кнопок
@router.callback_query(F.data == "subscribe_week")
async def subscribe_week(callback: CallbackQuery):
    await callback.answer("⏳ Функция оплаты в разработке", show_alert=True)

@router.callback_query(F.data == "subscribe_month")
async def subscribe_month(callback: CallbackQuery):
    await callback.answer("⏳ Функция оплаты в разработке", show_alert=True)