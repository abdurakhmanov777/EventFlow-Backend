import asyncio
from aiogram import Bot
import uvicorn
from fastapi import FastAPI
from app.database.models import async_main
from app.api import init_routers as init_routers_api
from app.routers import init_routers

from init_logger import LoguruLoggingMiddleware, logger
from app.database.requests import get_bots_startup
from config import BOT_TOKEN

from aiogram import Bot
from aiogram.types import BotCommand

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
        dp, polling_manager = init_routers()
        app = init_routers_api()

        # Только для основного бота
        await bots[0].get_updates(offset=-1)
        await set_bot_commands(bots[0])

        # Для остальных ботов только сбрасываем апдейты
        for bot in bots[1:]:
            await bot.get_updates(offset=-1)

        # Отключаем стандартный логгер FastAPI
        import logging
        logging.getLogger('uvicorn').disabled = True
        logging.getLogger('fastapi').disabled = True

        # Добавляем кастомное middleware для логирования
        app.add_middleware(LoguruLoggingMiddleware)

        logger.debug('Бот включен')

        # Запуск FastAPI
        config = uvicorn.Config(app, host='0.0.0.0', port=8000, log_level='critical')
        server = uvicorn.Server(config)

        await asyncio.gather(
            dp.start_polling(*bots, dp_for_new_bot=dp, polling_manager=polling_manager),
            server.serve()
        )

    except asyncio.CancelledError:
        logger.debug("Операция была отменена (например, по Ctrl+C)")
    except KeyboardInterrupt:
        logger.debug("Получен сигнал KeyboardInterrupt (Ctrl+C)")
    except Exception as e:
        logger.error(f"Необработанная ошибка: {e}")
    finally:
        logger.debug("Бот отключен")



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.debug("Главный цикл прерван (KeyboardInterrupt)")
