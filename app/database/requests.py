import asyncio
from app.database.models import UserApp, Bot, UserBot, Data, async_session
from sqlalchemy import select
from aiogram import Bot as Bot_aiogram

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

# async def add_bot(tg_id, name, api):
#     async with async_session() as session:
#         user = await session.scalar(select(UserApp).where(UserApp.tg_id == tg_id))
#         if user:
#             bot = await session.scalar(select(Bot).where(Bot.user_app_id == user.id))
#             if not bot:
#                 new_bot = Bot(name=name, api=api, user_app_id=user.id)
#                 session.add(new_bot)
#                 await session.commit()


async def add_bot(tg_id, name, api):
    async with async_session() as session:
        user = await session.scalar(select(UserApp).where(UserApp.tg_id == tg_id))
        if not user:
            await new_user(tg_id)
            user = await session.scalar(select(UserApp).where(UserApp.tg_id == tg_id))

        existing_bots = await session.execute(
            select(Bot).where((Bot.user_app_id == user.id) & ((Bot.name == name) | (Bot.api == api)))
        )
        existing_bots = existing_bots.scalars().all()

        if existing_bots:
            name_exists = any(bot.name == name for bot in existing_bots)
            api_exists = any(bot.api == api for bot in existing_bots)
            return {
                'status': False,
                'name': name_exists,
                'api': api_exists,
                'link': False,
            }

        bot = None  # Инициализируем заранее
        try:
            bot = Bot_aiogram(api)
            link = (await bot.get_me()).username

            session.add(Bot(
                name=name, api=api, user_app_id=user.id, link=link
            ))
            await session.commit()
            return {'status': True, 'link': link}
        except:
            return {
                'status': False,
                'name': False,
                'api': False
            }
        finally:
            if bot is not None:
                await bot.session.close()



async def delete_bot(tg_id, name):
    async with async_session() as session:
        user = await session.scalar(select(UserApp).where(UserApp.tg_id == tg_id))

        if not user:
            return False, {'status': False, 'error': 'User not found'}

        bot = await session.scalar(select(Bot).where(Bot.user_app_id == user.id, Bot.name == name))

        if not bot:
            return False, {'status': False, 'error': 'Bot not found'}

        bot_api = bot.api
        await session.delete(bot)
        await session.commit()

        return bot_api, {'status': True}




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
