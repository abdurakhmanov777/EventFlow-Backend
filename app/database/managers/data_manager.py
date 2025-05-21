from typing import Any
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from app.database.models import async_session, UserBot, Bot, Data


class DataService:
    '''Сервис для управления данными пользователя (таблица Data).'''

    @staticmethod
    async def _get_user_bot(session, tg_id: int, telegram_bot_id: int) -> UserBot | None:
        '''Вспомогательный метод для получения объекта UserBot.'''
        return await session.scalar(
            select(UserBot)
            .join(Bot)
            .where(UserBot.tg_id == tg_id, Bot.bot_id == telegram_bot_id)
        )

    @classmethod
    async def upsert(cls, tg_id: int, telegram_bot_id: int, name: str, value: any) -> bool:
        '''Добавляет или обновляет запись в таблице Data.'''
        try:
            async with async_session() as session:
                user_bot = await cls._get_user_bot(session, tg_id, telegram_bot_id)
                if not user_bot:
                    logger.warning(f'UserBot not found for tg_id={tg_id}, bot_id={telegram_bot_id}')
                    return False

                data_entry = await session.scalar(
                    select(Data)
                    .where(Data.user_bot_id == user_bot.id, Data.name == name)
                )

                if data_entry:
                    data_entry.value = value
                else:
                    session.add(Data(name=name, value=value, user_bot_id=user_bot.id))

                await session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f'Ошибка при upsert в Data: {e}')
            return False

    @classmethod
    async def get(cls, tg_id: int, telegram_bot_id: int, name: str) -> Any | None:
        '''Получает значение из таблицы Data по ключу name.'''
        try:
            async with async_session() as session:
                user_bot = await cls._get_user_bot(session, tg_id, telegram_bot_id)
                if not user_bot:
                    return None

                data_entry = await session.scalar(
                    select(Data)
                    .where(Data.user_bot_id == user_bot.id, Data.name == name)
                )

                return data_entry.value if data_entry else None
        except SQLAlchemyError as e:
            logger.error(f'Ошибка при получении Data: {e}')
            return None

    @classmethod
    async def delete(cls, tg_id: int, telegram_bot_id: int, name: str) -> bool:
        '''Удаляет запись из таблицы Data по ключу name.'''
        try:
            async with async_session() as session:
                user_bot = await cls._get_user_bot(session, tg_id, telegram_bot_id)
                if not user_bot:
                    return False

                data_entry = await session.scalar(
                    select(Data)
                    .where(Data.user_bot_id == user_bot.id, Data.name == name)
                )

                if data_entry:
                    await session.delete(data_entry)
                    await session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            logger.error(f'Ошибка при удалении Data: {e}')
            return False
