from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command, CommandObject
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import html_decoration as fmt
from aiogram.utils.token import TokenValidationError

# from app.modules.polling_manager import PollingManager
from app.routers.config import COMMAND_MAIN
from app.functions import keyboards as kb
from app.database import requests as rq
from app.utils.logger import log
from app.utils.time import time_now

router = Router()


@router.message(Command(*COMMAND_MAIN))
async def main(message: types.Message, state: FSMContext):
    key = message.text.lstrip('/').split()[0]
    loc = (await state.get_data()).get('loc')
    text = getattr(loc.default.text, key)
    keyboard = await kb.keyboard_dymanic(getattr(loc.default.keyboard, key))

    await message.answer(text=text, parse_mode='HTML', reply_markup=keyboard)
    await log(message)


@router.message(Command('gg'))
async def start(message: types.Message, state: FSMContext):
    loc = (await state.get_data()).get('loc')

    # state_name = 'state_2'
    # print(getattr(loc, state_name).type)

    # parts_text = loc.template.input.start
    # name = 'ФИО'
    # format = 'Иванов Иван Иванович'
    # text = f'{parts_text[0]}{name}{parts_text[1]}{format}{parts_text[2]}'

    parts_text = loc.template.input.saved
    name = 'ФИО'
    value = 'Абдурахманов Далгат Шамильевич'
    text = f'{parts_text[0]}{name}{parts_text[1]}{value}{parts_text[2]}'

    await message.answer(text=text, parse_mode='HTML')

    await log(message)


# @router.message(Command('addbot'))
# async def cmd_start(
#     message: types.Message,
#     command: CommandObject,
#     dp_for_new_bot: Dispatcher,
#     polling_manager: PollingManager
# ):
#     if command.args:
#         try:
#             bot = Bot(command.args)

#             if bot.id in polling_manager.polling_tasks:
#                 await message.answer('Bot with this id already running')
#                 return

#             # also propagate dp and polling manager to new bot to allow new bot add bots
#             polling_manager.start_bot_polling(
#                 dp=dp_for_new_bot,
#                 bot=bot,
#                 polling_manager=polling_manager,
#                 dp_for_new_bot=dp_for_new_bot,
#             )
#             bot_user = await bot.get_me()
#             # evbots.init_bot(bot, bot_user.username) # добавляешь в БД
#             await message.answer(f'New bot started: @{bot_user.username}')
#         except (TokenValidationError, TelegramUnauthorizedError) as err:
#             await message.answer(fmt.quote(f'{type(err).__name__}: {str(err)}'))
#     else:
#         await message.answer('Please provide token')


# @router.message(Command('stopbot'))
# async def cmd_start(message: types.Message, command: CommandObject, polling_manager: PollingManager,):

#     if command.args:
#         try:
#             polling_manager.stop_bot_polling(int(command.args))
#             # evbots.delete_bot(int(command.args)) # удаляешь из бд
#             await message.answer('Bot stopped')
#         except (ValueError, KeyError) as err:
#             await message.answer(fmt.quote(f'{type(err).__name__}: {str(err)}'))
#     else:
#         await message.answer('Please provide bot id')
