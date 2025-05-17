from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.utils.logger import log


def get_router_command() -> Router:
    router = Router()

    @router.message(Command('start'))
    async def multi_cmd(message: Message, state: FSMContext):
        loc = (await state.get_data()).get('loc')
        await message.answer(loc.state_1.type)
        await log(message)

    return router
