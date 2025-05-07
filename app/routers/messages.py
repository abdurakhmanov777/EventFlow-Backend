import re
from aiogram import Router, F
from loguru import logger
from aiogram import types
from aiogram.fsm.context import FSMContext

import app.database.requests as rq
import app.functions.keyboards as kb

from app.utils.logging import log
from app.utils.morphology import inflect_text, fix_preposition_o

# phrase = 'пальто'
# case = 'предложный'
# text = 'Нет информации о '
# if __name__ == '__main__':
#     result = text + inflect_text(phrase, case)
#     print(fix_preposition_o(result))

router = Router()

@router.message()
async def ckeck(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    try:
        mas = (message.text).split('\n')
        if len(mas) == 2:
            text = await fix_preposition_o(
                await inflect_text(mas[0], mas[1])
            )
        else:
            text = 'Неверный ввод'
        await message.answer(text)

        log(user_id, username)
    except Exception as error:
        log(user_id, username, error=error)


@router.message()
async def other(message: types.Message):
    pass
