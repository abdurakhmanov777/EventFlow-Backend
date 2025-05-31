import re

# from app.database.managers.data_manager import DataService as user_data
from app.database.requests import user_data, user_state
from app.modules.keyboards import keyboards as kb
from app.utils.morphology import process_text

async def create_msg(
    loc,
    state: str | int,
    tg_id: int,
    bot_id: int,
    input_data=False,
    select=False
):
    current = getattr(loc, state)
    msg_type, text = current.type, current.text

    if msg_type == 'select':
        text_msg = f'{loc.template.select[0]}{text}{loc.template.select[1]}'
        keyboard = await kb.multi_select(current.keyboard)

    elif msg_type == 'input':
        user_input = input_data or await user_data(
            tg_id=tg_id,
            bot_id=bot_id,
            action='get',
            name=text
        )

        if input_data and not re.fullmatch(current.pattern, input_data):
            err_prefix, err_suffix = loc.template.input.error
            return f'{err_prefix}{current.format}{err_suffix}', kb.multi_back

        if user_input:
            if input_data:
                await user_data(
                    tg_id=tg_id,
                    bot_id=bot_id,
                    action='upsert',
                    name=text,
                    value=input_data
                )

            saved = loc.template.input.saved
            text_msg = f'{saved[0]}{text}{saved[1]}{user_input}{saved[2]}'
            keyboard = await kb.multi_next(current.keyboard)
        else:
            start = loc.template.input.start
            formatted_text = await process_text(text, 'винительный', False)
            text_msg = f'{start[0]}{formatted_text}{start[1]}{current.format}{start[2]}'
            keyboard = kb.multi_back

    else:
        text_msg = text
        keyboard = await kb.multi_text(current.keyboard)

    if select:
        await user_data(
            tg_id=tg_id,
            bot_id=bot_id,
            action='upsert',
            name=getattr(loc, select[1]).text,
            value=select[0]
        )

    return text_msg, keyboard


async def data_output(
    tg_id: int,
    bot_id: int,
    loc
):
    states = await user_state(tg_id, bot_id, 'get')

    exclude = {'1', '99'}
    states = [s for s in states if s not in exclude]

    result = {
        getattr(loc, state).text: await user_data(tg_id, bot_id, name=getattr(loc, state).text)
        for state in states
    }

    items = '\n\n'.join(f'🔹️ {key}: {value}' for key, value in result.items())
    text_msg = (
        '<b><u>Проверьте свои данные</u></b>\n\n'
        f'<blockquote>{items}</blockquote>\n\n'
        '<i>Если всё верно, отправляйте данные для завершения регистрации.</i>'
    )

    return text_msg, kb.state_99


async def data_sending(
    tg_id: int,
    bot_id: int,
    loc
):

    text_msg = '100'
    return text_msg, None
