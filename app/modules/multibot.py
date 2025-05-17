import asyncio
from aiogram import Bot
from fastapi import HTTPException
from loguru import logger
from app.functions.commands import multibot_commands
from app.modules.polling_manager import PollingManager
from app.routers import create_router


async def _prepare_bot(api_token: str) -> Bot:
    bot = Bot(api_token)
    await bot.delete_webhook(drop_pending_updates=False)
    return bot


async def _start_polling(bot: Bot, polling_manager: PollingManager):
    dp = create_router()
    polling_manager.start_bot_polling(
        dp=dp,
        bot=bot,
        polling_timeout=10,
        handle_as_tasks=True
    )


async def _launch_bot(token: str, polling_manager: PollingManager):
    bot = await _prepare_bot(token)
    try:
        await _start_polling(bot, polling_manager)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота с токеном {token}: {e}")
    finally:
        await bot.session.close()


async def start_multiple_bots(api_tokens: list[str], polling_manager: PollingManager):
    """Параллельный запуск нескольких ботов"""
    await asyncio.gather(*[
        _launch_bot(token, polling_manager)
        for token in api_tokens
    ])


async def start_bot(api_token: str, polling_manager: PollingManager):
    bot = await _prepare_bot(api_token)
    try:
        await _start_polling(bot, polling_manager)
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
        raise HTTPException(status_code=400, detail="Invalid bot API token")
    finally:
        await bot.session.close()


async def get_bot_id_from_token(token: str) -> int:
    bot = Bot(token)
    try:
        return (await bot.get_me()).id
    finally:
        await bot.session.close()


async def stop_bot(api_token: str, polling_manager: PollingManager):
    try:
        bot_id = await get_bot_id_from_token(api_token)
        polling_manager.stop_bot_polling(bot_id)
    except Exception as e:
        logger.error(f"Ошибка остановки бота: {e}")
        raise HTTPException(status_code=400, detail="Failed to stop bot")
