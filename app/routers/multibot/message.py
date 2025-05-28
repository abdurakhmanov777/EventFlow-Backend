from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.modules.multibot.multi_handler import create_msg
from app.utils.logger import log
from app.database import rq_user

def get_router_message() -> Router:
    router = Router()

    @router.message()
    async def multi_msg(message: Message, state: FSMContext):
        data = await state.get_data()
        loc, bot_id = data.get('loc'), data.get('bot_id')

        state_db, msg_id = await rq_user.user_bot(
            tg_id=message.from_user.id,
            bot_id=bot_id
        )

        if getattr(loc, state_db).type != 'input':
            return

        text_msg, keyboard = await create_msg(
            loc, state_db, message.from_user.id, bot_id, input_data=message.text
        )

        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg_id,
                text=text_msg,
                parse_mode='HTML',
                reply_markup=keyboard
            )
        except:
            pass

        await log(message, info=state_db)

    @router.message()
    async def multi_delete(message: Message):
        await log(message)

    return router
