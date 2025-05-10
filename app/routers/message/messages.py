import re
from aiogram import Router, F
from loguru import logger
from aiogram import types
from aiogram.fsm.context import FSMContext

import app.database.requests as rq
import app.functions.keyboards as kb

from app.utils.logging import log
from app.utils.morphology import inflect_text, fix_preposition_o


router = Router()


# @router.message(lambda message: message.text and message.text.count('\n') == 1)
# async def ckeck(message: types.Message, state: FSMContext):
#     try:
#         mas = message.text.split('\n')
#         text = await fix_preposition_o(
#             await inflect_text(mas[0], mas[1])
#         )
#         await message.answer(text)

#         await log(message)
#     except Exception as error:
#         await log(message, error=error)


@router.message(lambda message: message.text and message.text.count('\n') == 1)
async def ckeck(message: types.Message, state: FSMContext):
    try:
        mas = message.text.split('\n')

        CASES = ['именительный', 'родительный', 'дательный', 'винительный', 'творительный', 'предложный']
        text = ''
        for elem in CASES:

            text += elem + ': ' + await fix_preposition_o(
                await inflect_text(mas[0], elem)
            ) + '\n'
        await message.answer(text)

        await log(message)
    except Exception as error:
        await log(message, error=error)


@router.message(lambda message: message.text and message.text.count('\n') == 0)
async def ckeck(message: types.Message, state: FSMContext):
    try:
        text1 = 'Введите ' + await fix_preposition_o(
            await inflect_text(message.text, 'винительный')
        )
        text2 = 'Нет информации ' + await fix_preposition_o(
            'о ' + await inflect_text(message.text, 'предложный')
        )
        await message.answer(f'{text1}\n{text2}')

        await log(message)
    except Exception as error:
        await log(message, error=error)


@router.message()
async def other(message: types.Message):
    pass
