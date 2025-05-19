from app.functions import keyboards as kb
from app.utils.morphology import process_text


async def create_msg(loc, state):
    current = getattr(loc, state)
    msg_type = current.type
    text = current.text
    keyboard = None

    if msg_type == 'text':
        text_msg = text
        keyboard = await kb.multi_text(current.keyboard)

    elif msg_type == 'input':
        data = 'Абдурахманов Далгат Шамильевич'
        # data = None
        if data:  # всегда будет False
            tmp = loc.template.input.saved
            text_msg = f'{tmp[0]}{text}{tmp[1]}{data}{tmp[2]}'
            keyboard = await kb.multi_next(current.keyboard)
        else:
            tmp = loc.template.input.start
            formatted_text = await process_text(text, 'винительный', False)
            text_msg = f'{tmp[0]}{formatted_text}{tmp[1]}{current.format}{tmp[2]}'
            keyboard = kb.multi_back

    else:  # selection
        keyboard = await kb.multi_select(current.keyboard)
        tmp = loc.template.selection
        text_msg = f'{tmp[0]}{text}{tmp[1]}'

    return text_msg, keyboard
