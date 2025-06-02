from typing import Any, Awaitable, Callable
from aiogram import BaseMiddleware, types, Bot
from aiogram.fsm.context import FSMContext

from app.database.requests import user_action
from app.modules.localization.localization import load_localization_multibot
from app.utils.logger import log_error


async def update_fsm_data(
    bot: Bot,
    state: FSMContext,
    user_id: int,
    extra_data: dict = None
) -> None:
    data = await state.get_data()
    if 'loc' in data:
        return

    lang = data.get('lang') or await user_action(tg_id=user_id, action='check', field='lang')
    loc = await load_localization_multibot(lang)
    bot_id = (await bot.get_me()).id

    await state.update_data(lang=lang, loc=loc, bot_id=bot_id, **(extra_data or {}))


async def safe_delete(message: types.Message):
    try:
        await message.delete()
    except Exception:
        pass


async def safe_delete_by_id(bot: Bot, chat_id: int, message_id: int):
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception:
        pass


class MwCommandMulti(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[types.Message, dict], Awaitable[Any]],
        event: types.Message,
        data: dict
    ) -> Any:
        try:
            if event.content_type != types.ContentType.TEXT:
                await safe_delete(event)
                return
            await update_fsm_data(data['bot'], data['state'], event.from_user.id)
            result = await handler(event, data)
            await safe_delete(event)

            if result:
                await safe_delete_by_id(event.bot, event.chat.id, result)

            return result
        except Exception as error:
            await log_error(event, error=error)


class MwMessageMulti(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[types.Message, dict], Awaitable[Any]],
        event: types.Message,
        data: dict
    ) -> Any:
        if event.content_type != types.ContentType.TEXT:
            await safe_delete(event)
            return

        try:
            await update_fsm_data(data['bot'], data['state'], event.from_user.id)
            result = await handler(event, data)
            await safe_delete(event)
            return result
        except Exception as error:
            await log_error(event, error=error)


class MwCallbackMulti(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[types.CallbackQuery, dict], Awaitable[Any]],
        event: types.CallbackQuery,
        data: dict
    ) -> Any:
        try:
            await update_fsm_data(data['bot'], data['state'], event.from_user.id)
            return await handler(event, data)
        except Exception as error:
            await log_error(event, error=error)
