import re
from aiogram.enums import ChatAction
from aiogram.types import CallbackQuery, Message, BufferedInputFile

from app.database.requests import user_bot, user_data, user_state
from app.modules.generator.main import create_text_image
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


from aiogram.types import CallbackQuery, Message
from aiogram.enums import ChatAction
from aiogram.types.input_file import BufferedInputFile
from io import BytesIO

async def data_sending(
    tg_id: int,
    bot_id: int,
    event: CallbackQuery | Message,
):
    # Определим бота и объект message вне зависимости от типа события
    bot = event.bot if isinstance(event, CallbackQuery) else event.bot
    message = event.message if isinstance(event, CallbackQuery) else event

    await bot.send_chat_action(chat_id=tg_id, action=ChatAction.UPLOAD_PHOTO)

    code = '1'
    try:
        buffer = await create_text_image(code)

        caption = (
            f'<b>Код участника: {code}</b>\n\n'
            '<i>Жди подтверждения участия, которое придёт ближе к дате мероприятия!</i>'
        )

        msg = await message.answer_photo(
            photo=BufferedInputFile(buffer.read(), filename="code.png"),
            caption=caption,
            parse_mode='HTML'
        )

        await bot.pin_chat_message(
            chat_id=message.chat.id,
            message_id=msg.message_id
        )

        await user_bot(tg_id=tg_id, bot_id=bot_id, action='upsert', msg_id=msg.message_id)

    except Exception as e:
        # Временно можно добавить print для отладки
        print(f"Ошибка в data_sending: {e}")

    finally:
        try:
            await message.delete()
        except:
            pass  # Сообщение могло быть уже удалено или не поддерживает удаление
