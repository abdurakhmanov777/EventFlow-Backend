from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from app.database import rq_user
from app.routers.multibot.multi_handler import create_msg
from app.utils.logger import log

def get_router_callback() -> Router:
    router = Router()

    @router.callback_query(lambda c: 'userstate_' in c.data)
    async def multi_clbk(callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        loc, bot_id = data.get('loc'), data.get('bot_id')

        _, next_state, *rest = callback.data.split('_')

        back_state = await rq_user.user_state(
            callback.from_user.id, bot_id, 'peekpush', next_state
        )
        select_param = (rest[0], back_state) if rest else None

        text_msg, keyboard = await create_msg(
            loc, next_state, callback.from_user.id, bot_id, select=select_param
        )
        await callback.message.edit_text(text=text_msg, parse_mode='HTML', reply_markup=keyboard)
        await log(callback, info=next_state)

    @router.callback_query(F.data == 'userback')
    async def multi_back(callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        loc, bot_id = data.get('loc'), data.get('bot_id')

        state_back = await rq_user.user_state(callback.from_user.id, bot_id, 'popeek')

        text_msg, keyboard = await create_msg(
            loc, state_back, callback.from_user.id, bot_id
        )

        try:
            await callback.message.edit_text(text=text_msg, parse_mode='HTML', reply_markup=keyboard)
        except:
            await callback.answer(
                'Сообщение не может быть обновлено. Введите команду /start',
                show_alert=True
            )

        await log(callback, info=state_back)

    return router
