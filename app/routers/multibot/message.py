from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.utils.logger import log


def get_router_message() -> Router:
    router = Router()

    @router.message()
    async def multi_msg(message: Message, state: FSMContext):
        loc = (await state.get_data()).get('loc')
        await message.answer(loc.state_1.type)
        await log(message)

    return router
