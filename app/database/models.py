from loguru import logger
from sqlalchemy import ARRAY, BigInteger, Boolean, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from config import DB_URL

engine = create_async_engine(url=DB_URL)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class UserApp(Base):
    '''Таблица пользователей приложения'''
    __tablename__ = 'user_app'

    id: Mapped[int] = mapped_column(primary_key=True)
    lang: Mapped[str] = mapped_column(String, default='ru')
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    bots = relationship('Bot', back_populates='user')


class Bot(Base):
    '''Таблица ботов'''
    __tablename__ = 'bot'

    id: Mapped[int] = mapped_column(primary_key=True)
    bot_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    link: Mapped[str] = mapped_column(String, nullable=False)
    api: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, default=False)
    settings: Mapped[str] = mapped_column(String, nullable=True)
    user_app_id: Mapped[int] = mapped_column(ForeignKey('user_app.id'))

    user = relationship('UserApp', back_populates='bots')
    user_bots = relationship('UserBot', back_populates='bot')


class UserBot(Base):
    '''Таблица пользователей бота'''
    __tablename__ = 'user_bot'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    msg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # state: Mapped[str] = mapped_column(String, default='1') # sqlite

    state: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        server_default=text("ARRAY['1']::varchar[]")
    )
    bot_id: Mapped[int] = mapped_column(ForeignKey('bot.id'))

    bot = relationship('Bot', back_populates='user_bots')
    data_entries = relationship('Data', back_populates='user_bot')


class Data(Base):
    '''Таблица данных'''
    __tablename__ = 'data'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[any] = mapped_column(JSONB, nullable=False)
    # value: Mapped[any] = mapped_column(String, nullable=False)
    user_bot_id: Mapped[int] = mapped_column(ForeignKey('user_bot.id'))

    user_bot = relationship('UserBot', back_populates='data_entries')


async def async_main():
    '''Создание таблиц в базе данных'''
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as error:
        logger.error(f'Ошибка: {error}')
