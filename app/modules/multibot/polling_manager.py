import asyncio
from asyncio import CancelledError, Task, get_running_loop
from contextvars import Context
from typing import Any, Awaitable, Dict, List, Optional
import logging

from aiogram import Bot
from aiogram.types import User
from aiogram.dispatcher.dispatcher import DEFAULT_BACKOFF_CONFIG, Dispatcher
from aiogram.utils.backoff import BackoffConfig

logger = logging.getLogger(__name__)


class PollingManager:
    def __init__(self):
        self.tasks: Dict[int, Task] = {}

    def active_bots_count(self) -> int:
        return len(self.tasks)

    def active_bot_ids(self) -> List[int]:
        return list(self.tasks)

    def start_bot_polling(
        self,
        dp: Dispatcher,
        bot: Bot,
        polling_timeout: int = 10,
        handle_as_tasks: bool = True,
        backoff_config: BackoffConfig = DEFAULT_BACKOFF_CONFIG,
        allowed_updates: Optional[List[str]] = None,
        on_bot_startup: Optional[Awaitable] = None,
        on_bot_shutdown: Optional[Awaitable] = None,
        **kwargs: Any,
    ):
        loop = get_running_loop()
        loop.call_soon(
            lambda: asyncio.create_task(
                self._run_polling(
                    dp, bot, polling_timeout, handle_as_tasks,
                    backoff_config, allowed_updates,
                    on_bot_startup, on_bot_shutdown, **kwargs
                )
            ),
            context=Context(),
        )

    async def _run_polling(
        self,
        dp: Dispatcher,
        bot: Bot,
        polling_timeout: int,
        handle_as_tasks: bool,
        backoff_config: BackoffConfig,
        allowed_updates: Optional[List[str]],
        on_bot_startup: Optional[Awaitable],
        on_bot_shutdown: Optional[Awaitable],
        **kwargs: Any,
    ):
        logger.info('Starting polling...')
        user: User = await bot.me()

        if on_bot_startup:
            await on_bot_startup

        try:
            logger.info('Polling bot @%s (id=%d, name=%r)', user.username, bot.id, user.full_name)
            task = asyncio.create_task(
                dp._polling(
                    bot=bot,
                    handle_as_tasks=handle_as_tasks,
                    polling_timeout=polling_timeout,
                    backoff_config=backoff_config,
                    allowed_updates=allowed_updates,
                    **kwargs,
                )
            )
            self.tasks[bot.id] = task
            await task
        except CancelledError:
            logger.info('Polling task was cancelled')
        finally:
            logger.info('Stopped polling bot @%s (id=%d)', user.username, bot.id)
            if on_bot_shutdown:
                await on_bot_shutdown
            await bot.session.close()
            self.tasks.pop(bot.id, None)

    def stop_bot_polling(self, bot_id: int):

        task = self.tasks.pop(bot_id, None)
        if task:
            task.cancel()


polling_manager = PollingManager()

def get_polling_manager() -> PollingManager:
    return polling_manager
