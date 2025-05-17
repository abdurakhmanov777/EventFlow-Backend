from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.utils.logger import log


def get_router_callback() -> Router:
    router = Router()

    @router.callback_query(F.data == 'delete')
    async def multi_delete(callback: CallbackQuery):
        await callback.message.delete()

        await log(callback)

    return router
