from loguru import logger

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def msg_new(user_id, text, markup):
    try:
        msg = await bot.send_message(
            chat_id=user_id,
            text = text,
            parse_mode='HTML',
            reply_markup=markup
        )
        return msg
    except Exception as error:
        logger.error(f'id = {user_id}, error = {error}')
        return False

async def delete(tg_id, msg_id):
    try:
        await bot.delete_message(tg_id, msg_id)
    except:
        pass

async def pin(user_id, msg_id):
    try:
        await bot.pin_chat_message(chat_id = user_id, message_id = msg_id)
    except:
        pass
