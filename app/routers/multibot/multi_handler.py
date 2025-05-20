import re
from app.functions import keyboards as kb
from app.utils.morphology import process_text


async def create_msg(loc, state: str | int, flag=False):
    current = getattr(loc, state)
    msg_type = current.type
    text = current.text
    keyboard = None

    # Обработка input-сообщения
    if msg_type == 'input' or flag:
        user_input = flag if flag else 'Абдурахманов Далгат Шамильевич'

        if flag and not re.fullmatch(current.pattern, flag):
            err_prefix, err_suffix = loc.template.input.error
            text_msg = f'{err_prefix}{current.format}{err_suffix}'
            keyboard = await kb.multi_next(current.keyboard)
            return text_msg, keyboard

        if user_input:
            saved_prefix, saved_middle, saved_suffix = loc.template.input.saved
            text_msg = f'{saved_prefix}{text}{saved_middle}{user_input}{saved_suffix}'
            keyboard = await kb.multi_next(current.keyboard)
        else:
            start_prefix, start_middle, start_suffix = loc.template.input.start
            formatted_text = await process_text(text, 'винительный', False)
            text_msg = f'{start_prefix}{formatted_text}{start_middle}{current.format}{start_suffix}'
            keyboard = kb.multi_back

    # Обработка простого текстового сообщения
    elif msg_type == 'text':
        text_msg = text
        keyboard = await kb.multi_text(current.keyboard)

    # Обработка выбора (selection)
    else:
        sel_prefix, sel_suffix = loc.template.selection
        text_msg = f'{sel_prefix}{text}{sel_suffix}'
        keyboard = await kb.multi_select(current.keyboard)

    return text_msg, keyboard
