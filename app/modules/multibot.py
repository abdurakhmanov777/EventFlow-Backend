from aiogram import Bot, Router
from aiogram.types import Message



from aiogram import Dispatcher
from fastapi import HTTPException
from loguru import logger
from app.modules.polling_manager import PollingManager
# from app.routers.command.command import router as command
# from app.routers.callback.callback import router as callback
# from app.routers.message.messages import router as messages
from app.middlewares.middlewares import MiddlewareCommand, MiddlewareMessage, MiddlewareCallback

def create_dispatcher_with_routes() -> Dispatcher:
    dp = Dispatcher()

    # Новые экземпляры роутеров
    command_router = create_command_router()
    # message_router = create_message_router()
    # callback_router = create_callback_router()

    # Middleware
    command_router.message.middleware(MiddlewareCommand())
    # message_router.message.middleware(MiddlewareMessage())
    # callback_router.callback_query.middleware(MiddlewareCallback())

    dp.include_router(command_router)
    # dp.include_router(message_router)
    # dp.include_router(callback_router)

    return dp


def create_command_router() -> Router:
    router = Router()

    @router.message()
    async def cmd_start(message: Message):
        await message.answer("Команда получена!")

    return router




async def start_multiple_bots(api_tokens: list, polling_manager: PollingManager):
    """Запуск нескольких ботов с переданными API токенами"""

    for api in api_tokens:
        bot = Bot(api)

        try:
            # Очищаем webhook и получаем информацию о боте
            await bot.delete_webhook(drop_pending_updates=False)
            # bot_user = await bot.get_me()

            dp = create_dispatcher_with_routes()

            polling_manager.start_bot_polling(dp=dp, bot=bot, polling_timeout=10, handle_as_tasks=True)

        except Exception as e:
            logger.error(f"Ошибка при запуске бота с API-ключом {api}: {e}")
            await bot.session.close()
            continue






async def get_bot_id_from_token(token: str) -> int:
    bot = Bot(token)
    try:
        bot_user = await bot.get_me()
        return bot_user.id
    finally:
        await bot.session.close()



async def start_bot(api: str, polling_manager: PollingManager):
    bot = Bot(api)
    try:
        await bot.delete_webhook(drop_pending_updates=False)
        dp = create_dispatcher_with_routes()
        polling_manager.start_bot_polling(dp=dp, bot=bot, polling_timeout=10, handle_as_tasks=True)
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
        raise HTTPException(status_code=400, detail="Invalid bot API token")
    finally:
        await bot.session.close()


async def stop_bot(api: str, polling_manager: PollingManager):
    try:
        bot_id = await get_bot_id_from_token(api)
        if bot_id is None:
            raise HTTPException(status_code=400, detail="Invalid bot ID")
        polling_manager.stop_bot_polling(bot_id)
    except Exception as e:
        logger.error(f"Ошибка остановки бота: {e}")
        raise HTTPException(status_code=400, detail="Failed to stop bot")
