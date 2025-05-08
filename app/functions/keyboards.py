from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

none = InlineKeyboardMarkup(inline_keyboard=[])


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

async def keyboard_dymanic(data: list[list[list[str]]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=txt,
                    url=rest[0] if typ == 'url' and rest else None,
                    web_app=WebAppInfo(url=rest[0]) if typ == 'webapp' and rest else None,
                    callback_data=None if typ in ['url', 'webapp'] else typ
                )
                for txt, typ, *rest in row
            ]
            for row in data
        ]
    )


async def keyboard(data: list[list[list[str]]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=txt,
                    callback_data=typ
                )
                for txt, typ in row
            ]
            for row in data
        ]
    )



async def toggle(data: list, flag: str) -> InlineKeyboardMarkup:
    '''Создает InlineKeyboardMarkup из вложенного списка.'''
    keyboard_buttons = []

    for item in data:
        label = item[0]
        value = item[1]

        if value == flag:
            text = f'{label} ✓'
        else:
            text = label

        button = InlineKeyboardButton(text=text, callback_data=value)
        keyboard_buttons.append([button])  # каждая кнопка в отдельной строке

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    return keyboard
