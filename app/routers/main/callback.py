from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from app.database.requests import user_action
import app.modules.keyboards.keyboards as kb
from app.routers.config import CALLBACK_MAIN, CALLBACK_SELECT
from app.modules.localization.localization import load_localization_main
from app.utils.logger import log


router = Router()


@router.callback_query(F.data == 'delete')
async def delete(callback: types.CallbackQuery):
    await callback.message.delete()

    await log(callback)



@router.callback_query(lambda c: c.data in CALLBACK_MAIN)
async def main(callback: types.CallbackQuery, state: FSMContext):
    loc = (await state.get_data()).get('loc')
    key = callback.data

    text = getattr(loc.default.text, key, '')
    keyboard = await kb.keyboard_dymanic(getattr(loc.default.keyboard, key, []))

    await callback.message.edit_text(text, parse_mode='HTML', reply_markup=keyboard)

    await log(callback)


@router.callback_query(lambda c: c.data in CALLBACK_SELECT)
async def select(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    loc = user_data.get('loc')
    key = callback.data
    current_value = user_data.get(key)

    text = getattr(loc.default.text, key)
    keyboard = await kb.toggle(getattr(loc.default.keyboard, key), f'select_{key}_{current_value}')

    await callback.message.edit_text(text=text, parse_mode='HTML', reply_markup=keyboard)

    await log(callback)


@router.callback_query(lambda c: c.data.startswith('select_') and len(c.data.split('_')) == 3)
async def option(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    _, key, value = callback.data.split('_')
    user_data = await state.get_data()

    if key:
        loc = await load_localization_main(value)
        await state.update_data(lang=value, loc=loc)
    else:
        loc = user_data.get('loc')

    text = getattr(loc.default.text, key)
    keyboard = await kb.toggle(getattr(loc.default.keyboard, key), callback.data)

    try:
        await callback.message.edit_text(text=text, parse_mode='HTML', reply_markup=keyboard)
        await state.update_data(**{key: value})
        await user_action(
            tg_id=callback.from_user.id,
            action='update',
            field=key,
            value=value
        )
    except:
        pass

    await log(callback)
