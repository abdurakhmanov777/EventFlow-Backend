from typing import Any, Awaitable, Callable
from aiogram import BaseMiddleware, types, Bot
from aiogram.fsm.context import FSMContext

from app.database.rq_user import user_action
from app.modules.localization.localization import load_localization_multibot
from app.utils.logger import log_error


async def update_fsm_data(
    bot: Bot,
    state: FSMContext,
    user_id: int,
    extra_data: dict = None
) -> None:
    user_data = await state.get_data()

    if 'loc' in user_data:
        return

    lang = user_data.get('lang') or await user_action(
        tg_id=user_id, action='check', field='lang'
    )
    loc = await load_localization_multibot(lang)
    bot_id = (await bot.get_me()).id

    update = {
        'lang': lang,
        'loc': loc,
        'bot_id': bot_id
    }

    if extra_data:
        update.update(extra_data)

    await state.update_data(**update)


class MwCommand_multi(BaseMiddleware):
    def __init__(self) -> None:
        self.counter = 0

    async def __call__(
        self,
        handler: Callable[[types.Message, dict], Awaitable[Any]],
        event: types.Message,
        data: dict
    ) -> Any:

        bot: Bot = data.get('bot')
        state: FSMContext = data.get('state')

        try:
            await update_fsm_data(bot, state, event.from_user.id)
            result = await handler(event, data)

            try:
                await event.delete()
            except Exception:
                pass

            if result:
                try:
                    await event.bot.delete_message(event.chat.id, result)
                except:
                    pass
        except Exception as error:
            await log_error(event, error=error)


class MwMessage_multi(BaseMiddleware):
    def __init__(self) -> None:
        self.counter = 0

    async def __call__(
        self,
        handler: Callable[[types.Message, dict], Awaitable[Any]],
        event: types.Message,
        data: dict
    ) -> Any:

        bot: Bot = data.get('bot')
        state: FSMContext = data.get('state')

        try:
            await update_fsm_data(bot, state, event.from_user.id)
            result = await handler(event, data)

            try:
                await event.delete()
            except Exception:
                pass

            return result
        except Exception as error:
            await log_error(event, error=error)


class MwCallback_multi(BaseMiddleware):
    def __init__(self) -> None:
        self.counter = 0

    async def __call__(
        self,
        handler: Callable[[types.CallbackQuery, dict], Awaitable[Any]],
        event: types.CallbackQuery,
        data: dict
    ) -> Any:

        bot: Bot = data.get('bot')
        state: FSMContext = data.get('state')

        try:
            await update_fsm_data(bot, state, event.from_user.id)
            result = await handler(event, data)
            return result
        except Exception as error:
            await log_error(event, error=error)
