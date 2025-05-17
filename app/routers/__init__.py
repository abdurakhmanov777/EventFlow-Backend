from aiogram import Dispatcher
from aiogram.fsm.storage.memory import SimpleEventIsolation

from app.routers.main.command import router as main_command
from app.routers.main.callback import router as main_callback
from app.routers.main.message import router as main_message

from app.routers.multibot.command import get_router_command
from app.routers.multibot.callback import get_router_callback
from app.routers.multibot.message import get_router_message

from app.middlewares.mw_main import MwCommand, MwMessage, MwCallback
from app.middlewares.mw_muti import MwCommand_multi, MwMessage_multi, MwCallback_multi
from app.modules.multibot.polling_manager import get_polling_manager


def _apply_middlewares(router_middleware_map: dict):
    for target, middleware in router_middleware_map.items():
        target.middleware(middleware)


def init_routers() -> tuple[Dispatcher, callable]:
    dp = Dispatcher(events_isolation=SimpleEventIsolation())

    _apply_middlewares({
        main_command.message: MwCommand(),
        main_message.message: MwMessage(),
        main_callback.callback_query: MwCallback(),
    })

    dp.include_routers(main_command, main_callback, main_message)
    return dp, get_polling_manager()


def create_router() -> Dispatcher:
    dp = Dispatcher(events_isolation=SimpleEventIsolation())

    router_command = get_router_command()
    router_callback = get_router_callback()
    router_message = get_router_message()

    _apply_middlewares({
        router_command.message: MwCommand_multi(),
        router_callback.callback_query: MwCallback_multi(),
        router_message.message: MwMessage_multi(),
    })

    dp.include_routers(router_command, router_callback, router_message)
    return dp
