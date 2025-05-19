import re
from aiogram import Router
from aiogram import types
from aiogram.fsm.context import FSMContext

import app.database.requests as rq
import app.functions.keyboards as kb

from app.utils.logger import log
from app.utils.morphology import process_text


router = Router()

@router.message(lambda message: message.text and message.text.count('\n') == 1)
async def ckeck(message: types.Message, state: FSMContext):
    mas = message.text.split('\n')

    CASES = ['именительный', 'родительный', 'дательный', 'винительный', 'творительный', 'предложный']
    text = ''
    for case in CASES:
        text_inflect = f'{case}: ' + await process_text(mas[0], case)
        text += f'{text_inflect}\n'
    await message.answer(text)

    await log(message)


@router.message(lambda message: message.text and message.text.count('\n') == 0)
async def ckeck(message: types.Message, state: FSMContext):
    text1 = 'Введите ' + await process_text(message.text, 'винительный')
    text2 = 'Нет информации о ' + await process_text(message.text, 'предложный')
    await message.answer(f'{text1}\n{text2}')

    await log(message)


@router.message()
async def other(message: types.Message):
    pass
