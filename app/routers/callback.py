import os
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from loguru import logger

import app.functions.keyboards as kb
import app.database.requests as rq
from app.utils.localization import load_localization

router = Router()



@router.callback_query(F.data == 'delete')
async def message_delete(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    try:
        await callback.message.delete()
        logger.info(f'start ({user_id}, {username})')
    except Exception as error:
        logger.error(f'start ({user_id}, {username}) {error})')


def list_main_commands(callback: types.CallbackQuery):
    list_callback_data = [
        'start',
        'settings'
    ]
    if callback.data in list_callback_data:
        return True
    return False


@router.callback_query(list_main_commands)
async def main_commands(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    username = callback.from_user.username

    try:
        user_data = await state.get_data()
        # await callback.answer(user_data.get('lang'), show_alert=True)
        loc = user_data.get('loc')
        key = callback.data
        text = getattr(loc.default.text, key)


        keyboard = await kb.keyboard(getattr(loc.default.keyboard, key))
        await callback.message.edit_text(text=text, parse_mode='HTML', reply_markup=keyboard)
        logger.info(f'main_commands ({user_id}, {username})')
    except Exception as error:
        logger.error(f'start ({user_id}, {username}) {error})')

@router.callback_query(F.data == 'lang')
async def toggle_check(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    username = callback.from_user.username

    try:
        user_data = await state.get_data()

        loc = user_data.get('loc')
        key = callback.data
        text = getattr(loc.default.text, key)

        keyboard = await kb.toggle(
            getattr(loc.default.keyboard, key),
            f'toggle_{callback.data}_{user_data.get(callback.data)}'
        )
        await callback.message.edit_text(text=text, parse_mode='HTML', reply_markup=keyboard)
        logger.info(f'start ({user_id}, {username})')
    except Exception as error:
        logger.error(f'start ({user_id}, {username}) {error})')



def toggle_check(callback: types.CallbackQuery):
    if 'toggle_' in callback.data and len((callback.data).split('_')) == 3:
        return True
    return False


@router.callback_query(toggle_check)
async def toggle(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    username = callback.from_user.username

    await callback.answer()
    try:
        data = (callback.data).split('_')
        user_data = await state.get_data()

        key = data[1]
        if data[1] == 'lang':
            loc = await load_localization(data[2])
        else:
            loc = user_data.get('loc')
        text = getattr(loc.default.text, key)

        keyboard = await kb.toggle(
            getattr(loc.default.keyboard, key),
            f'toggle_{data[1]}_{data[2]}'
        )
        # keyboard = kb.none
        try:
            await callback.message.edit_text(text=text, parse_mode='HTML', reply_markup=keyboard)
            # await state.update_data(lang=data[2])
            await state.update_data(**{data[1]: data[2]})
            await rq.user_update(user_id, data[1], data[2])
        except:
            print(111)
        logger.info(f'start ({user_id}, {username})')
    except Exception as error:
        logger.exception(f'start ({user_id}, {username}) {error})')

@router.callback_query(F.data == 'miniapp')
async def miniapp(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    username = callback.from_user.username
    try:
        user_data = await state.get_data()
        loc = user_data.get('loc')
        text = loc.default.text.miniapp

        keyboard = await kb.miniapp(
            loc.default.text.url_app,
            loc.default.keyboard.miniapp
        )
        await callback.message.edit_text(text=text, parse_mode='HTML', reply_markup=keyboard)
        logger.info(f'start ({user_id}, {username})')
    except Exception as error:
        logger.exception(f'start ({user_id}, {username}) {error})')
