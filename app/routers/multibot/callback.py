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
        callback_data = callback.data.split('_')
        next_state = callback_data[1]
        data = await state.get_data()
        loc, bot_id = data.get('loc'), data.get('bot_id')

        text_msg, keyboard = await create_msg(loc, callback_data[1])

        await callback.message.edit_text(
            text = text_msg,
            parse_mode = 'HTML',
            reply_markup=keyboard
        )

        await rq_user.user_state(
            callback.from_user.id, bot_id, 'push', next_state
        )

        print(await rq_user.user_state(callback.from_user.id, bot_id, 'get'))

        await log(callback)


    @router.callback_query(F.data == 'userback')
    async def multi_back(callback: CallbackQuery, state: FSMContext):
        await callback.answer()

        data = await state.get_data()
        loc, bot_id = data.get('loc'), data.get('bot_id')

        state_back = await rq_user.user_state(
            callback.from_user.id, bot_id, 'popeek'
        )

        states = await rq_user.user_state(
            callback.from_user.id, bot_id, 'get'
        )
        print(states)

        text_msg, keyboard = await create_msg(loc, state_back)
        try:
            await callback.message.edit_text(
                text = text_msg,
                parse_mode = 'HTML',
                reply_markup=keyboard
            )
        except:
            pass
        await log(callback)


    return router
