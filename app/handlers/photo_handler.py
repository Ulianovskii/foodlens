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
    
    result = await PromoService.activate_promo(promo_code, user_id)
    
    if result["success"]:
        await message.answer(
            i18n.get_text('promo_success', days=result["days"]),
            reply_markup=ReplyKeyboardRemove()
        )
        # Показываем обновленный профиль
        from app.handlers.basic_commands import cmd_profile
        await cmd_profile(message)
    else:
        error_text = {
            "invalid": i18n.get_text('promo_invalid'),
            "used": i18n.get_text('promo_already_used'),
            "expired": i18n.get_text('promo_expired')
        }.get(result["error"], "❌ Ошибка активации")
        
        await message.answer(error_text)
    
    await state.clear()