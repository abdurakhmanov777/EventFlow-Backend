from aiogram import Bot
from aiogram.types import BotCommand

async def bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запуск/перезапуск бота"),
        BotCommand(command="help", description="Техническая поддержка"),
    ]
    await bot.set_my_commands(commands)


async def multibot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запуск/перезапуск бота"),
        BotCommand(command="cancel", description="Отмена регистрации"),
        BotCommand(command="help", description="Контакты администратора"),
    ]
    await bot.set_my_commands(commands)
