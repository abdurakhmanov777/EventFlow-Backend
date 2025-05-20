import asyncio
from app.database.models import Bot, UserBot, async_session
from sqlalchemy import select

from app.database.state_manager import StateManager


async def new_user_bot(tg_id: int, telegram_bot_id: int, msg_id: int) -> tuple[str, int | None] | None:
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
            bot = await session.scalar(select(Bot).where(Bot.bot_id == telegram_bot_id))
            if not bot:
                return
            user_bot = UserBot(tg_id=tg_id, bot_id=bot.id, msg_id=msg_id)
            session.add(user_bot)

        await session.commit()
        await session.refresh(user_bot)

        return user_bot.state[-1], msg_old


async def check_state_and_msg_id(
    tg_id: int, telegram_bot_id: int
) -> tuple[str, int] | tuple[None, None]:
    async with async_session() as session:
        user_bot = await session.scalar(
            select(UserBot)
            .join(Bot)
            .where(UserBot.tg_id == tg_id, Bot.bot_id == telegram_bot_id)
        )
        if not user_bot:
            return

        return user_bot.state[-1], user_bot.msg_id

async def user_state(tg_id: int, bot_id: int, action: str = 'peek', value: str | None = None):
    async with async_session() as session:
        sm = StateManager(session, tg_id, bot_id)
        func = {
            'push': lambda: sm.push(value) if value else None,
            'pop': sm.pop,
            'peek': sm.peek,
            'popeek': sm.popeek,
            'get': sm.get_state,
            'clear': sm.clear,
        }.get(action)

        return await func() if func else None
