from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

none = InlineKeyboardMarkup(inline_keyboard=[])


async def keyboard(data: list[list[list[str]]]) -> InlineKeyboardMarkup:
    '''Создает InlineKeyboardMarkup из вложенного списка.'''
    keyboard_buttons = [
        [
            InlineKeyboardButton(
                text=item[0],
                callback_data=item[1]
            )
            for item in row
        ]
        for row in data
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    return keyboard


async def miniapp(url_app: str, data: list) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=data[0], web_app=WebAppInfo(url=url_app)
        )],
        [InlineKeyboardButton(
            text=data[1], callback_data='start'
        )]
    ])


async def toggle(data: list, flag: str) -> InlineKeyboardMarkup:
    '''Создает InlineKeyboardMarkup из вложенного списка.'''
    keyboard_buttons = []

    for item in data:
        label = item[0]
        value = item[1]

        if value == flag:
            text = f"{label} ✓"
        else:
            text = label

        button = InlineKeyboardButton(text=text, callback_data=value)
        keyboard_buttons.append([button])  # каждая кнопка в отдельной строке

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    return keyboard
