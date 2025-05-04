from typing import Any, Awaitable, Callable
from aiogram import BaseMiddleware, types

import app.database.requests as rq
from app.utils.localization import load_localization

async def update_language_data(event, data: dict) -> dict:
    state = data.get('state')

    lang = None

    if state:
        user_data = await state.get_data()
        lang = user_data.get('lang')

    # Если язык не найден в состоянии — проверим в БД
    if not lang:
        lang = await rq.user_check(event.from_user.id, 'lang')

    # Загружаем локализацию
    lang_data = await load_localization(lang)

    # Обновляем состояние
    if state:
        await state.update_data(lang=lang, loc=lang_data)

    return lang_data




class Middleware(BaseMiddleware):
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

        result = await handler(event, data)

        try:
            await event.delete()
        except Exception:
            pass

        return result


class MiddlewareCallback(BaseMiddleware):
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
        result = await handler(event, data)
        return result
