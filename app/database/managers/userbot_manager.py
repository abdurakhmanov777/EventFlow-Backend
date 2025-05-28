from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Bot, UserBot


class UserBotManager:
    def __init__(self, session: AsyncSession, tg_id: int, bot_ext_id: int):
        self.session = session
        self.tg_id = tg_id
        self.bot_ext_id = bot_ext_id  # внешний telegram_bot_id

    async def _get_user_bot(self) -> UserBot | None:
        stmt = (
            select(UserBot)
            .join(Bot)
            .where(UserBot.tg_id == self.tg_id, Bot.bot_id == self.bot_ext_id)
        )
        return await self.session.scalar(stmt)

    async def _get_bot(self) -> Bot | None:
        return await self.session.scalar(
            select(Bot).where(Bot.bot_id == self.bot_ext_id)
        )

    async def upsert_user_bot(self, msg_id: int) -> tuple[str, int | None] | None:
        try:
            user_bot = await self._get_user_bot()
            msg_old = None

            if user_bot:
                msg_old = user_bot.msg_id
                user_bot.msg_id = msg_id
            else:
                bot = await self._get_bot()
                if not bot:
                    return
                user_bot = UserBot(
                    tg_id=self.tg_id, bot_id=bot.id, msg_id=msg_id
                )
                self.session.add(user_bot)

            await self.session.commit()
            await self.session.refresh(user_bot)

            return user_bot.state[-1], msg_old
        except SQLAlchemyError:
            return False, False

    async def get_state_and_msg_id(self) -> tuple[str, int] | tuple[None, None] | bool:
        try:
            user_bot = await self._get_user_bot()
            if not user_bot:
                return None, None
            return user_bot.state[-1], user_bot.msg_id
        except SQLAlchemyError:
            return False
