from typing import List
from aiogram import Bot, Dispatcher
from loguru import logger
from app.routers.command.command import router as command
from app.routers.callback.callback import router as callback
from app.routers.message.messages import router as messages
from app.middlewares.middlewares import MiddlewareCommand, MiddlewareMessage, MiddlewareCallback

from aiogram.fsm.storage.memory import SimpleEventIsolation
from app.modules.polling_manager import polling_manager


dp = Dispatcher(events_isolation=SimpleEventIsolation())

# async def on_bot_startup(bot: Bot):
#     # await set_commands(bot)
#     print("Bot started!")
#     # await bot.send_message(chat_id=ADMIN_ID, text="Bot started!")


# async def on_bot_shutdown(bot: Bot):
#     print("Bot shutdown!")
#     # await bot.send_message(chat_id=ADMIN_ID, text="Bot shutdown!")

# async def on_startup(bots: List[Bot]):
#     logger.debug(f'Ботов включено: {len(bots)}')


# # выключение ботов
# async def on_shutdown(bots: List[Bot]):
#     logger.debug(f'Ботов отключено: {len(bots)}')
    # for bot in bots:
    #     await on_bot_shutdown(bot)


def init_routers():

    # Пары роутеров и соответствующих middleware
    middlewares = [
        (command.message, MiddlewareCommand()),
        (messages.message, MiddlewareMessage()),
        (callback.callback_query, MiddlewareCallback()),
    ]

    for target, middleware in middlewares:
        target.middleware(middleware)

    # Подключение всех роутеров
    for router in (callback, command, messages):
        dp.include_router(router)

    # dp.startup.register(on_startup)
    # dp.shutdown.register(on_shutdown)
    return dp, polling_manager
