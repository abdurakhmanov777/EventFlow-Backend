import re
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
# from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram import types
from aiogram.filters import Command, CommandObject
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.utils.markdown import html_decoration as fmt
from aiogram.utils.token import TokenValidationError
from aiogram.fsm.context import FSMContext

from app.modules.multibot.polling_manager import PollingManager
import app.database.requests as rq
import app.functions.keyboards as kb
from app.utils.logging import log

router = Router()


@router.message(Command('test'))
async def start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    try:
        user_data = await state.get_data()
        loc = user_data.get('loc')

        start_text = loc.default.text.test
        keyboard = await kb.miniapp(
            loc.default.text.url_test,
            loc.default.keyboard.miniapp
        )

        await message.answer(text=start_text, parse_mode='HTML', reply_markup=keyboard)

        log(user_id, username)
    except Exception as error:
        log(user_id, username, error=error)


@router.message(Command('help'))
async def help(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    try:
        user_data = await state.get_data()
        loc = user_data.get('loc')

        start_text = loc.default.text.help
        keyboard = kb.help

        await message.answer(text=start_text, parse_mode='HTML', reply_markup=keyboard)

        log(user_id, username)
    except Exception as error:
        log(user_id, username, error=error)


@router.message(Command('start'))
async def start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    try:
        user_data = await state.get_data()
        loc = user_data.get('loc')

        start_text = loc.default.text.start
        url_app = loc.default.text.url_app

        keyboard = await kb.keyboard(loc.default.keyboard.start)

        await message.answer(text=start_text, parse_mode='HTML', reply_markup=keyboard)

        log(user_id, username)
    except Exception as error:
        log(user_id, username, error=error)

@router.message(Command('miniapp'))
async def miniapp(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    try:
        user_data = await state.get_data()
        loc = user_data.get('loc')

        start_text = loc.default.text.start
        url_app = loc.default.text.url_app

        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(
                text='WebApp', web_app=types.WebAppInfo(url=url_app)
            )]]
        )

        await message.answer(text=start_text, parse_mode='HTML', reply_markup=keyboard)

        log(user_id, username)
    except Exception as error:
        log(user_id, username, error=error)

@router.message(Command('gg'))
async def start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    try:
        user_data = await state.get_data()
        loc = user_data.get('loc')

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

        log(user_id, username)
    except Exception as error:
        log(user_id, username, error=error)


@router.message(Command('addbot'))
async def cmd_start(message: types.Message, command: CommandObject,
    dp_for_new_bot: Dispatcher,
    polling_manager: PollingManager):
    if command.args:
        try:
            bot = Bot(command.args)

            if bot.id in polling_manager.polling_tasks:
                await message.answer('Bot with this id already running')
                return


            # also propagate dp and polling manager to new bot to allow new bot add bots
            polling_manager.start_bot_polling(
                dp=dp_for_new_bot,
                bot=bot,
                polling_manager=polling_manager,
                dp_for_new_bot=dp_for_new_bot,
            )
            bot_user = await bot.get_me()
            # evbots.init_bot(bot, bot_user.username) # добавляешь в БД
            await message.answer(f'New bot started: @{bot_user.username}')
        except (TokenValidationError, TelegramUnauthorizedError) as err:
            await message.answer(fmt.quote(f'{type(err).__name__}: {str(err)}'))
    else:
        await message.answer('Please provide token')


@router.message(Command('stopbot'))
async def cmd_start(message: types.Message, command: CommandObject, polling_manager: PollingManager,):

    if command.args:
        try:
            polling_manager.stop_bot_polling(int(command.args))
            # evbots.delete_bot(int(command.args)) # удаляешь из бд
            await message.answer('Bot stopped')
        except (ValueError, KeyError) as err:
            await message.answer(fmt.quote(f'{type(err).__name__}: {str(err)}'))
    else:
        await message.answer('Please provide bot id')
