from typing import Any, Awaitable, Callable
from aiogram import BaseMiddleware, types

import app.database.requests as rq
from app.modules.localization.localization import load_localization_main
from app.utils.logger import log_error

async def update_language_data(event, data: dict) -> dict:
    state = data['state']
    user_data = await state.get_data()

    if 'loc' in user_data:
        return

    lang = user_data.get('lang') or await rq.user_check(event.from_user.id, 'lang')
    await state.update_data(
        lang=lang,
        loc=await load_localization_main(lang)
    )






class MwCommand(BaseMiddleware):
    def __init__(self) -> None:
        self.counter = 0

    async def __call__(
        self,
        handler: Callable[[types.Message, dict], Awaitable[Any]],
        event: types.Message,
        data: dict
    ) -> Any:
        self.counter += 1
        data['counter'] = self.counter

        await update_language_data(event, data)
        try:
            result = await handler(event, data)
            try:
                await event.delete()
            except Exception:
                pass

            return result
        except Exception as error:
            await log_error(event, error=error)


class MwMessage(BaseMiddleware):
    def __init__(self) -> None:
        self.counter = 0

    async def __call__(
        self,
        handler: Callable[[types.Message, dict], Awaitable[Any]],
        event: types.Message,
        data: dict
    ) -> Any:
        self.counter += 1
        data['counter'] = self.counter

        await update_language_data(event, data)

        try:
            result = await handler(event, data)
            try:
                await event.delete()
            except Exception:
                pass

            return result
        except Exception as error:
            await log_error(event, error=error)


class MwCallback(BaseMiddleware):
    def __init__(self) -> None:
        self.counter = 0

    async def __call__(
        self,
        handler: Callable[[types.CallbackQuery, dict], Awaitable[Any]],
        event: types.CallbackQuery,
        data: dict
    ) -> Any:
        self.counter += 1
        data['counter'] = self.counter

        await update_language_data(event, data)

        try:
            result = await handler(event, data)

            return result
        except Exception as error:
            await log_error(event, error=error)
