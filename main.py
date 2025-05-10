import asyncio, logging, uvicorn
from aiogram import Bot
from aiogram.types import BotCommand

from app.api import init_routers as init_routers_api
from app.database.models import async_main
from app.database.requests import get_bots_startup
from app.routers import init_routers

from config import BOT_TOKEN
from init_logger import LoguruLoggingMiddleware, logger

async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запуск/перезапуск бота"),
        BotCommand(command="help", description="Техническая поддержка"),
    ]
    await bot.set_my_commands(commands)



async def main():
    try:
        await async_main()

        TOKENS = [BOT_TOKEN] + await get_bots_startup()
        bots = [Bot(token) for token in TOKENS]

        # Сброс апдейтов и установка команд для первого бота
        for i, bot in enumerate(bots):
            await bot.delete_webhook()
            await bot.get_updates(offset=-1)
            if i == 0:
                await set_bot_commands(bot)


        dp, polling_manager = init_routers()
        app = init_routers_api()

        # Отключаем стандартный логгер FastAPI
        logging.getLogger('uvicorn').disabled = True
        logging.getLogger('fastapi').disabled = True

        # Добавляем кастомный middleware
        app.add_middleware(LoguruLoggingMiddleware)

        logger.debug('Бот включен')

        # Настройка и запуск FastAPI и Aiogram
        config = uvicorn.Config(app, host='0.0.0.0', port=8000, log_level='critical')
        server = uvicorn.Server(config)

        await asyncio.gather(
            dp.start_polling(*bots, dp_for_new_bot=dp, polling_manager=polling_manager),
            server.serve()
        )

    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.debug("Завершение работы по сигналу отмены или Ctrl+C")
    except Exception as e:
        logger.error(f"Необработанная ошибка: {e}")
    finally:
        logger.debug("Бот отключен")




if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.debug("Главный цикл прерван (KeyboardInterrupt)")
