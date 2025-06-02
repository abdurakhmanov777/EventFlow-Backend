from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.modules.keyboards.keyboards import help
from app.modules.multibot.multi_handler import create_msg, data_output, data_sending
from app.utils.logger import log
from app.database.requests import user_bot, user_data, user_state


def get_router_command() -> Router:
    router = Router()

    async def update_state(message: Message, state: FSMContext):
        data = await state.get_data()
        tg_id = message.from_user.id
        bot_id = data.get('bot_id')
        msg_id = message.message_id + 1

        state_db, old_msg_id = await user_bot(
            tg_id=tg_id,
            bot_id=bot_id,
            action='upsert',
            msg_id=msg_id
        )

        return tg_id, bot_id, data.get('loc'), state_db, old_msg_id

    @router.message(Command('start'))
    async def multi_cmd(message: Message, state: FSMContext):
        tg_id, bot_id, loc, state_db, old_msg_id = await update_state(message, state)

        if state_db == '100':
            await data_sending(tg_id, bot_id, message)
        elif state_db == '99':
            text_msg, keyboard = await data_output(tg_id, bot_id, loc)
            await message.answer(text=text_msg, parse_mode='HTML', reply_markup=keyboard)
        else:
            text_msg, keyboard = await create_msg(loc, state_db, tg_id, bot_id)
            await message.answer(text=text_msg, parse_mode='HTML', reply_markup=keyboard)

        if old_msg_id:
            try:
                await message.bot.delete_message(message.chat.id, old_msg_id)
            except:
                pass

        await log(message, info=state_db)

    @router.message(Command('cancel'))
    async def multi_cancel(message: Message, state: FSMContext):
        tg_id, bot_id, loc, _, old_msg_id = await update_state(message, state)

        await user_data(tg_id, bot_id, 'delete_all')
        await user_state(tg_id, bot_id, 'clear')

        text_msg, keyboard = await create_msg(loc, '1', tg_id, bot_id)

        await message.answer(text=text_msg, parse_mode='HTML', reply_markup=keyboard)

        if old_msg_id:
            try:
                await message.bot.delete_message(message.chat.id, old_msg_id)
            except:
                pass

        await log(message)

    @router.message(Command('help'))
    async def multi_help(message: Message, state: FSMContext):
        loc = (await state.get_data()).get('loc')

        await message.answer(text=loc.help, parse_mode='HTML', reply_markup=help)
        await log(message)

    return router
