import asyncio
from asyncio import Task
from typing import Any, Awaitable, Dict, List, Optional
from loguru import logger

from aiogram import Bot
from aiogram.types import User
from aiogram.dispatcher.dispatcher import DEFAULT_BACKOFF_CONFIG, Dispatcher
from aiogram.utils.backoff import BackoffConfig

class PollingManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.api_to_bot_id: Dict[str, int] = {}

    def active_bots_count(self) -> int:
        return len(self.tasks)

    def active_api_tokens(self) -> List[str]:
        return list(self.tasks.keys())

    def start_bot_polling(
        self,
        dp: Dispatcher,
        api_token: str,
        polling_timeout: int = 10,
        handle_as_tasks: bool = True,
        backoff_config: BackoffConfig = DEFAULT_BACKOFF_CONFIG,
        allowed_updates: Optional[List[str]] = None,
        on_bot_startup: Optional[Awaitable] = None,
        on_bot_shutdown: Optional[Awaitable] = None,
        **kwargs: Any,
    ):
        if self.is_bot_running(api_token):
            return

        task = asyncio.create_task(
            self._run_polling(
                dp=dp,
                api_token=api_token,
                polling_timeout=polling_timeout,
                handle_as_tasks=handle_as_tasks,
                backoff_config=backoff_config,
                allowed_updates=allowed_updates,
                on_bot_startup=on_bot_startup,
                on_bot_shutdown=on_bot_shutdown,
                **kwargs
            )
        )
        self.tasks[api_token] = task

    async def _run_polling(
        self,
        dp: Dispatcher,
        api_token: str,
        polling_timeout: int,
        handle_as_tasks: bool,
        backoff_config: BackoffConfig,
        allowed_updates: Optional[List[str]],
        on_bot_startup: Optional[Awaitable],
        on_bot_shutdown: Optional[Awaitable],
        **kwargs: Any,
    ):
        async with Bot(api_token) as bot:
            try:
                await bot.delete_webhook(drop_pending_updates=False)
                user: User = await bot.me()
                self.api_to_bot_id[api_token] = user.id

                if on_bot_startup:
                    await on_bot_startup

                await dp._polling(
                    bot=bot,
                    handle_as_tasks=handle_as_tasks,
                    polling_timeout=polling_timeout,
                    backoff_config=backoff_config,
                    allowed_updates=allowed_updates,
                    **kwargs,
                )

            except Exception as error:
                logger.exception(f'Unexpected error in polling task for token {api_token}: {error}')

            finally:
                if on_bot_shutdown:
                    await on_bot_shutdown
                self.tasks.pop(api_token, None)
                self.api_to_bot_id.pop(api_token, None)

    def stop_bot_polling(self, api_token: str):
        task = self.tasks.get(api_token)
        if task and not task.done():
            task.cancel()

    def is_bot_running(self, api_token: str) -> bool:
        task = self.tasks.get(api_token)
        return task is not None and not task.done()


polling_manager = PollingManager()

def get_polling_manager() -> PollingManager:
    return polling_manager
