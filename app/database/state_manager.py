import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from app.database.models import Bot, UserBot

class StateManager:
    def __init__(self, session: AsyncSession, tg_id: int, bot_id: int):
        self.session = session
        self.tg_id = tg_id
        self.bot_id = bot_id

    async def _get_user_bot(self) -> UserBot | None:
        stmt = (
            select(UserBot)
            .join(Bot)
            .where(UserBot.tg_id == self.tg_id, Bot.bot_id == self.bot_id)
        )
        return await self.session.scalar(stmt)

    async def get_state(self) -> list[str]:
        user_bot = await self._get_user_bot()
        # Возвращаем state или ['1'], если state пустой или None
        if not user_bot or not user_bot.state:
            return ['1']
        return user_bot.state

    async def push(self, value: str):
        user_bot = await self._get_user_bot()
        if user_bot:
            if not user_bot.state:
                user_bot.state = ['1']
            user_bot.state.append(value)
            flag_modified(user_bot, 'state')
            await self.session.commit()

    async def pop(self) -> str | None:
        user_bot = await self._get_user_bot()
        if not (user_bot and user_bot.state):
            return None

        if len(user_bot.state) == 1:
            return user_bot.state[0]
        value = user_bot.state.pop()
        flag_modified(user_bot, 'state')
        await self.session.commit()
        return value

    async def peek(self) -> str | None:
        user_bot = await self._get_user_bot()
        if user_bot and user_bot.state:
            return user_bot.state[-1]
        return None

    async def popeek(self) -> str:
        user_bot = await self._get_user_bot()
        if not (user_bot and user_bot.state):
            return None

        if len(user_bot.state) == 1:
            return user_bot.state[0]
        value = user_bot.state[-2]
        user_bot.state.pop()
        flag_modified(user_bot, 'state')
        await self.session.commit()
        return value


    async def clear(self):
        user_bot = await self._get_user_bot()
        if user_bot:
            user_bot.state = ['1']
            flag_modified(user_bot, 'state')
            await self.session.commit()



# class StateManager:
#     DELIMITER = '|'

#     def __init__(self, session: AsyncSession, tg_id: int, bot_id: int):
#         self.session = session
#         self.tg_id = tg_id
#         self.bot_id = bot_id

#     async def _get_user_bot(self) -> UserBot | None:
#         stmt = (
#             select(UserBot)
#             .join(Bot)
#             .where(UserBot.tg_id == self.tg_id, Bot.bot_id == self.bot_id)
#         )
#         return await self.session.scalar(stmt)

#     def _deserialize(self, state_str: str | None) -> list[str]:
#         return state_str.split(self.DELIMITER) if state_str else []

#     def _serialize(self, state_list: list[str]) -> str:
#         return self.DELIMITER.join(state_list)

#     async def get_state(self) -> list[str]:
#         user_bot = await self._get_user_bot()
#         return self._deserialize(user_bot.state) if user_bot else []

#     async def push(self, value: str):
#         user_bot = await self._get_user_bot()
#         if user_bot:
#             state_list = self._deserialize(user_bot.state)
#             state_list.append(value)
#             user_bot.state = self._serialize(state_list)
#             flag_modified(user_bot, 'state')
#             await self.session.commit()

#     async def pop(self) -> str | None:
#         user_bot = await self._get_user_bot()
#         if not user_bot:
#             return None
#         state_list = self._deserialize(user_bot.state)
#         if not state_list:
#             return None
#         value = state_list.pop()
#         user_bot.state = self._serialize(state_list)
#         flag_modified(user_bot, 'state')
#         await self.session.commit()
#         return value

#     async def peek(self) -> str | None:
#         user_bot = await self._get_user_bot()
#         if not user_bot:
#             return None
#         state_list = self._deserialize(user_bot.state)
#         return state_list[-1] if state_list else None

#     async def clear(self):
#         user_bot = await self._get_user_bot()
#         if user_bot:
#             user_bot.state = ''
#             flag_modified(user_bot, 'state')
#             await self.session.commit()
