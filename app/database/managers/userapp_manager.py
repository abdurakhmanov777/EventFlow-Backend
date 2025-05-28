import asyncio

from aiogram import Bot as Bot_aiogram
from sqlalchemy import select

from app.database.models import Bot, Data, UserApp, UserBot, async_session
from app.modules.keyboards.commands import multibot_commands


class UserService:
    def __init__(self, session, tg_id: int):
        self.session = session
        self.tg_id = tg_id

    async def _get_user(self):
        return await self.session.scalar(select(UserApp).where(UserApp.tg_id == self.tg_id))

    async def new_user(self):
        user = await self._get_user()
        if not user:
            new_user = UserApp(tg_id=self.tg_id)
            self.session.add(new_user)
            await self.session.commit()
            return 'ru'
        return user.lang

    async def update_field(self, field_name: str, new_value):
        user = await self._get_user()
        if user:
            setattr(user, field_name, new_value)
            await self.session.commit()
            return True
        return False

    async def check_field(self, field_name: str):
        user = await self._get_user()
        if user:
            return getattr(user, field_name)
        return await self.new_user()

    async def add_bot(self, name: str, api: str):
        user = await self._get_user()
        if not user:
            await self.new_user()
            user = await self._get_user()

        name_exists = await self.session.scalar(
            select(Bot).where(Bot.user_app_id == user.id, Bot.name == name)
        )
        api_exists = await self.session.scalar(
            select(Bot).where(Bot.api == api)
        )

        if name_exists or api_exists:
            return {
                'status': False,
                'name': name_exists is not None,
                'api': api_exists is not None,
                'link': False,
            }

        try:
            async with Bot_aiogram(api) as bot:
                bot_data = await bot.get_me()
                new_bot = Bot(
                    name=name,
                    api=api,
                    user_app_id=user.id,
                    link=bot_data.username,
                    bot_id=bot_data.id,
                )
                self.session.add(new_bot)
                await self.session.commit()
                asyncio.create_task(self._run_bot_tasks(Bot_aiogram(api)))  # новый экземпляр для задач
                return {'status': True, 'link': bot_data.username}
        except Exception:
            return {'status': False, 'name': False, 'api': False}


    async def _run_bot_tasks(self, bot):
        try:
            await multibot_commands(bot)
        finally:
            await bot.session.close()

    async def delete_bot(self, name: str):
        user = await self._get_user()
        if not user:
            return False, {'status': False, 'error': 'User not found'}

        bot = await self.session.scalar(
            select(Bot).where(Bot.user_app_id == user.id, Bot.name == name)
        )
        if not bot:
            return False, {'status': False, 'error': 'Bot not found'}

        user_bots = await self.session.scalars(select(UserBot).where(UserBot.bot_id == bot.id))
        for user_bot in user_bots.all():
            data_entries = await self.session.scalars(select(Data).where(Data.user_bot_id == user_bot.id))
            for data_entry in data_entries.all():
                await self.session.delete(data_entry)
            await self.session.delete(user_bot)

        bot_api, bot_status = bot.api, bot.status
        await self.session.delete(bot)
        await self.session.commit()

        return bot_api, bot_status, {'status': True}

    async def get_user_bots(self):
        user = await self._get_user()
        if not user:
            await self.new_user()
            return []

        query = select(Bot.name, Bot.api, Bot.link, Bot.status).where(Bot.user_app_id == user.id)
        result = await self.session.execute(query)
        return [
            {'name': name, 'api': api, 'link': link, 'status': status}
            for name, api, link, status in result.fetchall()
        ]

    async def update_bot_field(self, api: str, field_name: str, new_value):
        user = await self._get_user()
        if not user:
            return False

        bot = await self.session.scalar(select(Bot).where(Bot.api == api))
        if bot:
            setattr(bot, field_name, new_value)
            name = bot.name
            link = bot.link
            await self.session.commit()
            return {
                'status': new_value,
                'name': name,
                'link': link,
                'api': api
            }
        return False

class BotStatusService:
    @staticmethod
    async def get_active_apis() -> list[str]:
        async with async_session() as session:
            query = select(Bot.api).where(Bot.status == True)
            result = await session.execute(query)
            return result.scalars().all()
