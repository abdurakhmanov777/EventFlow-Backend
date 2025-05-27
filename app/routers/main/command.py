from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.routers.config import COMMAND_MAIN
from app.functions import keyboards as kb
from app.utils.logger import log

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

    parts_text = loc.template.input.saved
    name = 'ФИО'
    value = 'Абдурахманов Далгат Шамильевич'
    text = f'{parts_text[0]}{name}{parts_text[1]}{value}{parts_text[2]}'

    await message.answer(text=text, parse_mode='HTML')

    await log(message)
