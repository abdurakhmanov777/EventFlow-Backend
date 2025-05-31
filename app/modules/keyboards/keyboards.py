from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from config import SYMB

none = InlineKeyboardMarkup(inline_keyboard=[])

help = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
    text='Закрыть окно',
    callback_data='delete'
)]])

state_99 = InlineKeyboardMarkup(
    inline_keyboard=[
        # [InlineKeyboardButton(text='Отправить данные', callback_data=f'userstate{SYMB}100')],
        [InlineKeyboardButton(text='Отправить данные', callback_data=f'userstate_100')],
        [InlineKeyboardButton(text='Назад', callback_data='userback')]
    ]
)

async def keyboard_dynamic(data: list[list[list[str]]]) -> InlineKeyboardMarkup:
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
            [InlineKeyboardButton(text=txt, callback_data=typ) for txt, typ in row]
            for row in data
        ]
    )


async def toggle(data: list, flag: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f'{label} ✓' if value == flag else label,
                callback_data=value
            )]
            for label, value in data
        ]
    )


async def keyboard_user(data: list[list[list[str]]], state) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton(text=txt, callback_data=f'state{SYMB}{typ}') for txt, typ in row]
        for row in data
    ]
    inline_keyboard.append([InlineKeyboardButton(text='Назад', callback_data=f'state_{state}')])
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


async def multi_next(next_state: str | int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Далее', callback_data=f'userstate{SYMB}{next_state}')],
            [InlineKeyboardButton(text='Назад', callback_data='userback')]
        ]
    )

multi_back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='userback')]
])


async def multi_text(next_state, text: str = 'Даю согласие') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=f'userstate{SYMB}{next_state}')]
        ]
    )


async def multi_select(data: list[list[str]]) -> InlineKeyboardMarkup:
    long_buttons = []
    short_buttons = []

    for txt, state, flag_db in data:
        button = InlineKeyboardButton(
            text=txt,
            callback_data=f'userstate{SYMB}{state}{SYMB}{txt}{SYMB}{flag_db}'
        )
        if len(txt) > 13:
            long_buttons.append([button])  # одиночная строка
        else:
            short_buttons.append(button)   # парные строки

    # Сгруппируем короткие кнопки по 2 в ряд
    short_rows = [short_buttons[i:i+2] for i in range(0, len(short_buttons), 2)]

    keyboard = long_buttons + short_rows  # длинные — сверху, короткие — снизу
    keyboard.append([InlineKeyboardButton(text='Назад', callback_data='userback')])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
