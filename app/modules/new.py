from aiogram import Bot, Router
from aiogram.types import Message



from aiogram import Dispatcher
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
            await bot.delete_webhook(drop_pending_updates=True)
            # bot_user = await bot.get_me()

            # Создаём dispatcher с маршрутизаторами
            dp = create_dispatcher_with_routes()

            # Запуск polling для бота
            polling_manager.start_bot_polling(dp=dp, bot=bot, polling_timeout=10, handle_as_tasks=True)

        except Exception as e:
            logger.error(f"Ошибка при запуске бота с API-ключом {api}: {e}")
            await bot.session.close()  # Закрываем сессию бота при ошибке
            # Пропуск этого бота, если произошла ошибка
            continue

    # После запуска всех ботов, логируем количество активных ботов
    # logger.info(f"Всего запущено ботов: {polling_manager.active_bots_count()}")
    # logger.debug(f"Активные боты: {polling_manager.active_bot_ids()}")




async def stop_multiple_bots(api_tokens: list, polling_manager: PollingManager):
    """Остановка нескольких ботов"""

    for api in api_tokens:
        try:
            bot_id = await get_bot_id_from_token(api)
            polling_manager.stop_bot_polling(bot_id)

            bot = Bot(api)
            await polling_manager.close_bot_session(bot)  # Закрытие сессии

            logger.info(f"Бот с id={bot_id} успешно остановлен")

        except Exception as e:
            logger.error(f"Ошибка остановки бота с API {api}: {e}")


async def get_bot_id_from_token(token: str) -> int:
    bot = Bot(token)
    try:
        bot_user = await bot.get_me()
        return bot_user.id
    finally:
        await bot.session.close()
