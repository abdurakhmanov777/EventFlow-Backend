import asyncio
from typing import Any
from app.database.models import Bot, Data, UserBot, async_session
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.database.managers.state_manager import StateManager


async def new_user_bot(
    tg_id: int,
    telegram_bot_id: int,
    msg_id: int
) -> tuple[str, int | None] | None:
    try:
        async with async_session() as session:
            user_bot = await session.scalar(
                select(UserBot)
                .join(Bot)
                .where(UserBot.tg_id == tg_id, Bot.bot_id == telegram_bot_id)
            )

            msg_old = None

            if user_bot:
                msg_old = user_bot.msg_id
                user_bot.msg_id = msg_id
            else:
                bot = await session.scalar(
                    select(Bot).where(Bot.bot_id == telegram_bot_id)
                )
                if not bot:
                    return
                user_bot = UserBot(
                    tg_id=tg_id, bot_id=bot.id, msg_id=msg_id)
                session.add(user_bot)

            await session.commit()
            await session.refresh(user_bot)

            return user_bot.state[-1], msg_old
    except SQLAlchemyError:
        return False, False


async def check_state_and_msg_id(
    tg_id: int,
    telegram_bot_id: int
) -> tuple[str, int] | tuple[None, None]:
    try:
        async with async_session() as session:
            user_bot = await session.scalar(
                select(UserBot)
                .join(Bot)
                .where(UserBot.tg_id == tg_id, Bot.bot_id == telegram_bot_id)
            )
            if not user_bot:
                return

            return user_bot.state[-1], user_bot.msg_id
    except SQLAlchemyError:
        return False

async def user_state(
    tg_id: int,
    bot_id: int,
    action: str = 'peek',
    value: str | None = None
):
    try:
        async with async_session() as session:
            sm = StateManager(session, tg_id, bot_id)
            func = {
                'push': lambda: sm.push(value) if value else None,
                'pop': sm.pop,
                'peek': sm.peek,
                'peekpush': lambda: sm.peekpush(value) if value else None,
                'popeek': sm.popeek,
                'get': sm.get_state,
                'clear': sm.clear,
            }.get(action)

            return await func() if func else None
    except SQLAlchemyError:
        return False


async def upsert_data(
    tg_id: int,
    telegram_bot_id: int,
    name: str,
    value: any
) -> bool:
    try:
        async with async_session() as session:
            # Получаем UserBot через Bot
            user_bot = await session.scalar(
                select(UserBot)
                .join(Bot)
                .where(UserBot.tg_id == tg_id, Bot.bot_id == telegram_bot_id)
            )

            if not user_bot:
                return False

            # Ищем существующую запись Data с нужным name
            data_entry = await session.scalar(
                select(Data)
                .where(Data.user_bot_id == user_bot.id, Data.name == name)
            )

            if data_entry:
                # Обновляем значение
                data_entry.value = value
            else:
                # Добавляем новую запись
                data_entry = Data(name=name, value=value, user_bot_id=user_bot.id)
                session.add(data_entry)

            await session.commit()
            return True
    except SQLAlchemyError:
        return False


async def get_data_value(
    tg_id: int,
    telegram_bot_id: int,
    name: str
) -> Any | None:
    try:
        async with async_session() as session:
            user_bot = await session.scalar(
                select(UserBot)
                .join(Bot)
                .where(UserBot.tg_id == tg_id, Bot.bot_id == telegram_bot_id)
            )

            if not user_bot:
                return None

            data_entry = await session.scalar(
                select(Data)
                .where(Data.user_bot_id == user_bot.id, Data.name == name)
            )

            return data_entry.value if data_entry else None
    except SQLAlchemyError:
        return None
