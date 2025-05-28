from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.functions.keyboards import help
from app.modules.multibot.multi_handler import create_msg
from app.utils.logger import log
from app.database.requests import user_bot


def get_router_command() -> Router:
    router = Router()

    @router.message(Command('start'))
    async def multi_cmd(message: Message, state: FSMContext):
        data = await state.get_data()
        loc, bot_id = data.get('loc'), data.get('bot_id')

        state_db, msg_id = await user_bot(
            tg_id=message.from_user.id,
            bot_id=bot_id,
            action='upsert',
            msg_id=message.message_id+1
        )

        text_msg, keyboard = await create_msg(
            loc, state_db, message.from_user.id, bot_id
        )
        await message.answer(
            text=text_msg,
            parse_mode='HTML',
            reply_markup=keyboard
        )

        if msg_id:
            try:
                await message.bot.delete_message(message.chat.id, msg_id)
            except:
                pass

        await log(message, info=state_db)

    @router.message(Command('help'))
    async def multi_cmd(message: Message, state: FSMContext):
        data = await state.get_data()
        loc = data.get('loc')

        await message.answer(
            text=loc.help,
            parse_mode='HTML',
            reply_markup=help
        )

        await log(message)

    return router
