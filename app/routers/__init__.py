from typing import List
from aiogram import Bot, Dispatcher
from loguru import logger
from app.routers.commands import router as commands
from app.routers.callback import router as callback
from app.routers.messages import router as messages
from app.middlewares.middlewares import MiddlewareCommand, MiddlewareMessage, MiddlewareCallback

from aiogram.fsm.storage.memory import SimpleEventIsolation
from app.modules.multibot.polling_manager import PollingManager

# async def on_bot_startup(bot: Bot):
#     # await set_commands(bot)
#     print("Bot started!")
#     # await bot.send_message(chat_id=ADMIN_ID, text="Bot started!")


# async def on_bot_shutdown(bot: Bot):
#     print("Bot shutdown!")
#     # await bot.send_message(chat_id=ADMIN_ID, text="Bot shutdown!")

async def on_startup(bots: List[Bot]):
    logger.debug(f'Ботов включено: {len(bots)}')


# выключение ботов
async def on_shutdown(bots: List[Bot]):
    logger.debug(f'Ботов отключено: {len(bots)}')
    # for bot in bots:
    #     await on_bot_shutdown(bot)


def init_routers() -> Dispatcher:
    dp = Dispatcher(events_isolation=SimpleEventIsolation())

    commands.message.middleware(MiddlewareCommand())
    messages.message.middleware(MiddlewareMessage())
    callback.callback_query.middleware(MiddlewareCallback())

    dp.include_router(commands)
    dp.include_router(callback)
    dp.include_router(messages)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    polling_manager = PollingManager()

    return dp, polling_manager
