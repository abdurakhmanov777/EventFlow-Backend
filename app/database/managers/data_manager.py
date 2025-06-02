from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Bot, Data, UserBot



class DataManager:
    def __init__(self, session: AsyncSession, tg_id: int, bot_id: int):
        self.session = session
        self.tg_id = tg_id
        self.bot_id = bot_id

    async def _get_user_bot(self) -> UserBot | None:
        stmt = (
            select(UserBot)
            .options(selectinload(UserBot.data_entries))
            .join(Bot)
            .where(UserBot.tg_id == self.tg_id, Bot.bot_id == self.bot_id)
        )
        return await self.session.scalar(stmt)

    async def get(self, name: str) -> Any | None:
        user_bot = await self._get_user_bot()
        if not user_bot:
            return None
        stmt = select(Data).where(Data.user_bot_id == user_bot.id, Data.name == name)
        data_entry = await self.session.scalar(stmt)
        return data_entry.value if data_entry else None

    async def upsert(self, name: str, value: Any) -> bool:
        user_bot = await self._get_user_bot()
        if not user_bot:
            return False

        stmt = select(Data).where(Data.user_bot_id == user_bot.id, Data.name == name)
        data_entry = await self.session.scalar(stmt)

        if data_entry:
            data_entry.value = value
        else:
            self.session.add(Data(name=name, value=value, user_bot_id=user_bot.id))

        await self.session.commit()
        return True

    async def delete(self, name: str) -> bool:
        user_bot = await self._get_user_bot()
        if not user_bot:
            return False

        stmt = select(Data).where(Data.user_bot_id == user_bot.id, Data.name == name)
        data_entry = await self.session.scalar(stmt)

        if data_entry:
            await self.session.delete(data_entry)
            await self.session.commit()
            return True

        return False

    async def delete_all(self) -> bool:
        user_bot = await self._get_user_bot()
        if not user_bot:
            return False

        stmt = delete(Data).where(Data.user_bot_id == user_bot.id)
        await self.session.execute(stmt)
        await self.session.commit()
        return True
