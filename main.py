import asyncio, logging, uvicorn
from aiogram import Bot

from app.routers.__init_http__ import init_routers as init_routers_http
from app.database.models import async_main
from app.database.requests import get_bots_startup
from app.functions.commands import bot_commands
from app.modules.multibot.bot_manager import start_multiple_bots
from app.modules.multibot.polling_manager import get_polling_manager
from app.routers.__init_bot__ import init_routers

from config import BOT_TOKEN
from app.utils.logger import LoguruLoggingMiddleware, logger


async def main():
    try:
        # Инициализация базы данных
        await async_main()

        main_bot = Bot(BOT_TOKEN)
        await main_bot.delete_webhook()
        await main_bot.get_updates(offset=-1)
        await bot_commands(main_bot)


        dp, polling_manager = init_routers()

        # Запуск всех созданных ботов
        TOKENS = await get_bots_startup()
        await start_multiple_bots(TOKENS, polling_manager)

        # Отключаем стандартный логгер FastAPI
        logging.getLogger('uvicorn').disabled = True
        logging.getLogger('fastapi').disabled = True

        # Добавляем кастомный middleware
        app = init_routers_http()
        app.add_middleware(LoguruLoggingMiddleware)

        logger.debug(f'Ботов включено: 1 / {len(TOKENS)}')

        # Настройка и запуск FastAPI и Aiogram
        config = uvicorn.Config(app, host='0.0.0.0', port=8000, log_level='critical')
        server = uvicorn.Server(config)

        await asyncio.gather(
            # Первый бот работает с основным dp
            dp.start_polling(*[main_bot], dp_for_new_bot=dp, polling_manager=polling_manager),
            server.serve()
        )

    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.debug("Завершение работы по сигналу отмены или Ctrl+C")
    except Exception as e:
        logger.error(f"Необработанная ошибка: {e}")
    finally:
        TOKENS = get_polling_manager().active_bots_count()
        logger.debug(f'Ботов отключено: 1 / {TOKENS}')



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.debug("Главный цикл прерван (KeyboardInterrupt)")
