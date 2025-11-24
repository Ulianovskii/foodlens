from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.services.promo_service import PromoService
from app.services.user_service import UserService
from app.core.i18n import get_localization

router = Router()

class PromoStates(StatesGroup):
    waiting_for_promo = State()

@router.callback_query(F.data == "enter_promo")
async def enter_promo(callback: CallbackQuery, state: FSMContext):
    i18n = get_localization()
    await callback.message.answer(
        i18n.get_text('promo_enter'),
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(PromoStates.waiting_for_promo)
    await callback.answer()

@router.message(StateFilter(PromoStates.waiting_for_promo))
async def process_promo(message: Message, state: FSMContext):
    i18n = get_localization()
    promo_code = message.text.strip().upper()
    user_id = message.from_user.id
    
    try:
        # Получаем пользователя
        user_service = UserService(message.bot.user_service.database)
        user = await user_service.get_or_create_user(
            telegram_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        # Активируем промокод
        promo_service = PromoService(message.bot.user_service.database)
        success = await promo_service.activate_promo_code(promo_code, user)
        
        if success:
            # Обновляем данные пользователя
            user = await user_service.get_or_create_user(user_id)
            
            await message.answer(
                i18n.get_text('promo_activated').format(
                    subscription_type=user.subscription_type,
                    until=user.subscription_until.strftime("%d.%m.%Y") if user.subscription_until else "не указано"
                ),
                reply_markup=ReplyKeyboardRemove()
            )
            # Показываем обновленный профиль
            from app.handlers.basic_commands import cmd_profile
            await cmd_profile(message)
        else:
            await message.answer(i18n.get_text('promo_invalid'))
    
    except Exception as e:
        logger.error(f"Ошибка активации промокода: {e}")
        await message.answer("❌ Произошла ошибка при активации промокода")
    
    await state.clear()

# Обработчики для кнопок подписки (временно заглушки)
@router.callback_query(F.data == "subscribe_week")
async def subscribe_week(callback: CallbackQuery):
    i18n = get_localization()
    await callback.answer("⏳ Функция оплаты в разработке", show_alert=True)

@router.callback_query(F.data == "subscribe_month")
async def subscribe_month(callback: CallbackQuery):
    i18n = get_localization()
    await callback.answer("⏳ Функция оплаты в разработке", show_alert=True)