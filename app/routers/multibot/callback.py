from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from app.database.requests import user_state
from app.modules.multibot.multi_handler import create_msg, data_output, data_sending
from app.utils.logger import log
from config import SYMB

def get_router_callback() -> Router:
    router = Router()

    @router.callback_query(F.data == 'delete')
    async def multi_delete(callback: CallbackQuery):
        await callback.message.delete()

        await log(callback)


    @router.callback_query(lambda c: f'userstate{SYMB}' in c.data)
    async def multi_clbk(callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        loc, bot_id = data.get('loc'), data.get('bot_id')
        tg_id = callback.from_user.id
        _, next_state, *rest = callback.data.split(SYMB)
        back_state = await user_state(
            tg_id, bot_id, 'peekpush', next_state
        )

        if next_state == '99':
            text_msg, keyboard = await data_output(
                tg_id, bot_id, loc
            )

        # elif next_state == '100':
        #     text_msg, keyboard = await data_sending(
        #         tg_id, bot_id, loc
        #     )

        else:
            select_param = (rest[0], back_state) if (rest and rest[1] == 'True') else None

            text_msg, keyboard = await create_msg(
                loc, next_state, tg_id, bot_id, select=select_param
            )
        await callback.message.edit_text(text=text_msg, parse_mode='HTML', reply_markup=keyboard)
        await log(callback, info=next_state)

    @router.callback_query(F.data == 'userback')
    async def multi_back(callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        loc, bot_id = data.get('loc'), data.get('bot_id')
        tg_id = callback.from_user.id

        state_back = await user_state(tg_id, bot_id, 'popeek')

        text_msg, keyboard = await create_msg(
            loc, state_back, tg_id, bot_id
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
