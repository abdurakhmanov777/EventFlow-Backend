import asyncio
from app.database.models import UserApp, Bot, UserBot, Data, async_session
from sqlalchemy import select
from aiogram import Bot as Bot_aiogram

from app.functions.commands import multibot_commands

async def new_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(UserApp).where(UserApp.tg_id == tg_id))
        if not user:
            new_user = UserApp(tg_id=tg_id)
            session.add(new_user)
            await session.commit()
            return 'ru'
        return user.lang


async def user_update(tg_id, field_name, new_value):
    async with async_session() as session:
        user = await session.scalar(select(UserApp).where(UserApp.tg_id == tg_id))
        if user:
            setattr(user, field_name, new_value)
            await session.commit()
            return True

async def user_check(tg_id, field_name):
    async with async_session() as session:
        user = await session.scalar(select(UserApp).where(UserApp.tg_id == tg_id))
        if user:
            return getattr(user, field_name)
        else:
            return await new_user(tg_id)


async def add_bot(tg_id, name, api):
    async with async_session() as session:

        user = await session.scalar(select(UserApp).where(UserApp.tg_id == tg_id))
        if not user:
            await new_user(tg_id)
            user = await session.scalar(select(UserApp).where(UserApp.tg_id == tg_id))

        # Проверка: есть ли такой name у этого пользователя
        name_exists = await session.scalar(
            select(Bot).where(Bot.user_app_id == user.id, Bot.name == name)
        )

        # Проверка: есть ли такой api в любой записи в базе
        api_exists = await session.scalar(
            select(Bot).where(Bot.api == api)
        )

        if name_exists or api_exists:
            return {
                'status': False,
                'name': name_exists is not None,
                'api': api_exists is not None,
                'link': False,
            }

        bot = None
        try:
            bot = Bot_aiogram(api)
            bot_data = await bot.get_me()
            link = bot_data.username
            bot_id = bot_data.id
            session.add(Bot(
                name=name, api=api, user_app_id=user.id, link=link, bot_id=bot_id
            ))
            await session.commit()
            asyncio.create_task(run_bot_tasks(bot))
            return {'status': True, 'link': link}
        except:
            return {
                'status': False,
                'name': False,
                'api': False
            }

async def run_bot_tasks(bot):
    try:
        await multibot_commands(bot)
    finally:
        await bot.session.close()



async def delete_bot(tg_id, name):
    async with async_session() as session:
        user = await session.scalar(select(UserApp).where(UserApp.tg_id == tg_id))

        if not user:
            return False, {'status': False, 'error': 'User not found'}

        bot = await session.scalar(select(Bot).where(Bot.user_app_id == user.id, Bot.name == name))

        if not bot:
            return False, {'status': False, 'error': 'Bot not found'}

        # Получаем список пользователей этого бота
        user_bots = await session.scalars(select(UserBot).where(UserBot.bot_id == bot.id))
        user_bots = user_bots.all()  # превращаем в список

        # Удаляем все данные (Data) каждого пользователя бота и затем пользователей бота
        for user_bot in user_bots:
            data_entries = await session.scalars(select(Data).where(Data.user_bot_id == user_bot.id))
            data_entries = data_entries.all()  # тоже список

            for data_entry in data_entries:
                await session.delete(data_entry)

            await session.delete(user_bot)

        bot_api, bot_on = bot.api, bot.status

        # Удаляем самого бота
        await session.delete(bot)
        await session.commit()

        return bot_api, bot_on, {'status': True}






async def get_user_bots(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(UserApp).where(UserApp.tg_id == tg_id))

        if not user:
            await new_user(tg_id)
            return []

        query = select(
            Bot.name, Bot.api, Bot.link, Bot.status
        ).join(UserApp).where(UserApp.id == user.id)

        result = await session.execute(query)
        bots_data = result.fetchall()

        return [{
            'name': bot_data[0],
            'api': bot_data[1],
            'link': bot_data[2],
            'status': bot_data[3]
            # 'status': bot_data
        } for bot_data in bots_data]


async def user_update_bot(tg_id, api, field_name, new_value):
    async with async_session() as session:
        user = await session.scalar(select(UserApp).where(UserApp.tg_id == tg_id))
        if user:
            bot = await session.scalar(select(Bot).where(Bot.api == api))
            if bot:
                setattr(bot, field_name, new_value)
                name = bot.name
                link = bot.link
                await session.commit()
                return {
                    'status': new_value,
                    'name': name,
                    'link': link,
                    'api': api
                }
    return False


async def get_bots_startup():
    async with async_session() as session:
        query = select(Bot.api).where(Bot.status == True)
        result = await session.execute(query)
        return result.scalars().all()
