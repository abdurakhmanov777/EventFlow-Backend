from typing import Any

from sqlalchemy import select
from app.database.managers.data_manager import DataManager
from app.database.managers.userapp_manager import BotStatusService, UserService
from app.database.managers.userbot_manager import UserBotManager
from app.database.models import async_session
from sqlalchemy.exc import SQLAlchemyError

from app.database.managers.state_manager import StateManager


async def get_active_bot_apis() -> list[str]:
    return await BotStatusService.get_active_apis()


async def user_action(tg_id: int, action: str, **kwargs):
    try:
        async with async_session() as session:
            service = UserService(session, tg_id)
            actions = {
                'new': service.new_user,
                'update': lambda: service.update_field(kwargs['field'], kwargs['value']),
                'check': lambda: service.check_field(kwargs['field']),
                'add_bot': lambda: service.add_bot(kwargs['name'], kwargs['api']),
                'delete_bot': lambda: service.delete_bot(kwargs['name']),
                'get_bots': service.get_user_bots,
                'update_bot': lambda: service.update_bot_field(kwargs['api'], kwargs['field'], kwargs['value'])
            }
            func = actions.get(action)
            return await func() if func else None
    except SQLAlchemyError:
        return False


async def user_bot(
    tg_id: int,
    bot_id: int,
    action: str = 'check',
    msg_id: int | None = None,
):
    try:
        async with async_session() as session:
            ubm = UserBotManager(session, tg_id, bot_id)
            func = {
                'upsert': lambda: ubm.upsert_user_bot(msg_id) if msg_id is not None else None,
                'check': ubm.get_state_and_msg_id,
            }.get(action)
            return await func() if func else None
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


async def user_data(
    tg_id: int,
    bot_id: int,
    action: str = 'get',
    name: str | None = None,
    value: Any = None
):
    try:
        async with async_session() as session:
            dm = DataManager(session, tg_id, bot_id)
            func = {
                'get': lambda: dm.get(name) if name else None,
                'upsert': lambda: dm.upsert(name, value) if name and value is not None else None,
                'delete': lambda: dm.delete(name) if name else None,
            }.get(action)

            return await func() if func else None
    except SQLAlchemyError:
        return False
