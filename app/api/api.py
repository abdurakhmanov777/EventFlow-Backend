import asyncio
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
from aiogram import F, Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from fastapi import Depends

from app.modules.new import create_dispatcher_with_routes
from app.modules.polling_manager import PollingManager
import app.database.requests as rq
from config import BOT_TOKEN

from app.modules.polling_manager import get_polling_manager

from app.routers.command.command import router as command
from app.routers.callback.callback import router as callback
from app.routers.message.messages import router as messages
from app.middlewares.middlewares import MiddlewareCommand, MiddlewareMessage, MiddlewareCallback


router = APIRouter()
bot = Bot(token=BOT_TOKEN)

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
}

def cors_response():
    return JSONResponse(content={}, headers=CORS_HEADERS)

@router.options('/bot/{action}')
async def preflight():
    return cors_response()


@router.post('/bot/create_new_bot')
async def create_new_bot(request: Request):
    try:
        data = await request.json()
        name, api, user_id = data.get('name'), data.get('api'), data.get('user_id')

        if not user_id:
            raise HTTPException(status_code=401, detail='Authorization error')
        if not all([name, api]):
            raise HTTPException(status_code=400, detail='Incorrect data')

        result = await rq.add_bot(user_id, name, api)
        return JSONResponse(content=result, headers=CORS_HEADERS)
    except Exception as error:
        logger.error(f'Ошибка при обработке запроса от {user_id}: {error}')
        raise HTTPException(status_code=500, detail='Internal server error')


# @router.post('/bot/toggle_lang')
# async def toggle_lang(request: Request):
#     try:
#         data = await request.json()
#         value, user_id = data.get('value'), data.get('user_id')

#         if not user_id:
#             raise HTTPException(status_code=401, detail='Authorization error')
#         if not value:
#             raise HTTPException(status_code=400, detail='Incorrect data')

#         result = await rq.user_update(user_id, 'lang', value)
#         return JSONResponse(content=result, headers=CORS_HEADERS)
#     except Exception as error:
#         logger.error(f'Ошибка при обработке запроса от {user_id}: {error}')
#         raise HTTPException(status_code=500, detail='Internal server error')

@router.post('/bot/delete_bot')
async def delete_bot(request: Request):
    try:
        data = await request.json()
        name, user_id = data.get('name'), data.get('user_id')

        if not user_id:
            raise HTTPException(status_code=401, detail='Authorization error')
        if not name:
            raise HTTPException(status_code=400, detail='Incorrect data')

        result = await rq.delete_bot(user_id, name)
        return JSONResponse(content=result, headers=CORS_HEADERS)
    except Exception as error:
        logger.error(f'Ошибка при обработке запроса от {user_id}: {error}')
        raise HTTPException(status_code=500, detail='Internal server error')


@router.post('/bot/get_bot_list')
async def get_bot_list(request: Request):
    try:
        data = await request.json()
        user_id = data.get('user_id')

        if not user_id:
            raise HTTPException(status_code=401, detail='Authorization error')

        bot_list = await rq.get_user_bots(user_id)
        return JSONResponse(content=bot_list, headers=CORS_HEADERS)
    except Exception as error:
        logger.error(f'Error fetching bot list: {error}')
        raise HTTPException(status_code=500, detail='Internal server error')



@router.post('/bot/toggle_bot')
async def receive_bot_name(
    request: Request, polling_manager: PollingManager = Depends(get_polling_manager)
):
    try:
        data = await request.json()
        value, api, user_id = data.get('value'), data.get('api'), data.get('user_id')

        if not user_id:
            logger.warning("Ошибка авторизации: отсутствует user_id")
            raise HTTPException(status_code=401, detail='Authorization error')

        # Обновление статуса пользователя в базе данных
        result = await rq.user_update_bot(user_id, api, 'status', value == 'on')

        if value == 'on':
            bot = Bot(api)

            try:
                await bot.delete_webhook(drop_pending_updates=True)
                bot_user = await bot.get_me()
                # logger.info(f"Бот API подтверждён: @{bot_user.username}")

                dp = create_dispatcher_with_routes()

                polling_manager.start_bot_polling(dp=dp, bot=bot, polling_timeout=10, handle_as_tasks=True)

                # logger.info(f"Бот @{bot_user.username} успешно запущен")
            except Exception as e:
                logger.error(f"Ошибка проверки API-ключа: {e}")
                await bot.session.close()
                raise HTTPException(status_code=400, detail="Invalid bot API token")

        else:
            try:
                bot_id = await get_bot_id_from_token(api)
                if bot_id is None:
                    raise HTTPException(status_code=400, detail="Invalid bot ID")


                # Останавливаем polling для бота с полученным ID
                polling_manager.stop_bot_polling(bot_id)

                # Закрываем сессию бота напрямую
                bot = Bot(api)
                await bot.session.close()  # Закрытие сессии бота

                # logger.info(f"Бот с id={bot_id} успешно остановлен")

            except Exception as e:
                logger.error(f"Ошибка остановки бота с API {api}: {e}")
                raise HTTPException(status_code=400, detail="Failed to stop bot")


        return JSONResponse(content=result, headers=CORS_HEADERS)

    except Exception as error:
        logger.error(f'Ошибка при обработке запроса от {data.get("user_id", "неизвестен")}: {error}')
        raise HTTPException(status_code=500, detail='Internal server error')


async def get_bot_id_from_token(token: str) -> int:
    try:
        bot = Bot(token)
        bot_user = await bot.get_me()
        return bot_user.id
    except Exception as e:
        logger.error(f"Ошибка получения ID бота с токеном {token}: {e}")
        return None
    finally:
        await bot.session.close()


# @router.post('/bot/t')
# async def receive_bot_name(
#     request: Request,
#     polling_manager: PollingManager = Depends(lambda: polling_manager)
# ):
#     try:
#         data = await request.json()
#         value, api, user_id = data.get('value'), data.get('api'), data.get('user_id')

#         if not user_id:
#             logger.warning("Ошибка авторизации: отсутствует user_id")
#             raise HTTPException(status_code=401, detail='Authorization error')

#         if value == 'on':
#             bot = Bot(api)
#             try:
#                 bot_user = await bot.get_me()
#                 logger.info(f"Бот API подтверждён: @{bot_user.username}")

#                 dp = Dispatcher()

#                 # Здесь вызываем синхронную функцию без await
#                 polling_manager.start_bot_polling(dp=dp, bot=bot, polling_timeout=10, handle_as_tasks=True)

#                 logger.info(f"Бот @{bot_user.username} успешно запущен")
#             except Exception as e:
#                 logger.error(f"Ошибка проверки API-ключа: {e}")
#                 # Закрываем сессию бота в случае ошибки
#                 await bot.session.close()
#                 raise HTTPException(status_code=400, detail="Invalid bot API token")



#         result = await rq.user_update_bot(user_id, api, 'status', value == 'on')
#         return JSONResponse(content=result, headers=CORS_HEADERS)

#     except Exception as error:
#         logger.error(f'Ошибка при обработке запроса от {user_id}: {error}')
#         raise HTTPException(status_code=500, detail='Internal server error')




# @router.message(Command("addbot"))
@router.post('/bot/addbot')
async def receive_bot_name(request: Request):
    try:
        data = await request.json()
        api, user_id = data.get('api'), data.get('user_id')
        bot = Bot(api)

        # if bot.id in PollingManager.polling_tasks:
        #     await message.answer("Bot with this id already running")
        #     return


        # also propagate dp and polling manager to new bot to allow new bot add bots
        PollingManager.start_bot_polling(
            dp=Dispatcher,
            bot=bot,
            polling_manager=PollingManager,
            dp_for_new_bot=Dispatcher,
        )
        bot_user = await bot.get_me()
        # # evbots.init_bot(bot, bot_user.username) # добавляешь в БД
        # await message.answer(f"New bot started: @{bot_user.username}")
    except Exception as error:
        logger.error(f'Ошибка при обработке запроса от {user_id}: {error}')
        raise HTTPException(status_code=500, detail='Internal server error')

# async def cmd_start(message: types.Message, command: CommandObject,
#     dp_for_new_bot: Dispatcher,
#     polling_manager: PollingManager,):
#     if command.args:
#         try:
#             bot = Bot(command.args)

#             if bot.id in polling_manager.polling_tasks:
#                 await message.answer("Bot with this id already running")
#                 return


#             # also propagate dp and polling manager to new bot to allow new bot add bots
#             polling_manager.start_bot_polling(
#                 dp=dp_for_new_bot,
#                 bot=bot,
#                 polling_manager=polling_manager,
#                 dp_for_new_bot=dp_for_new_bot,
#             )
#             bot_user = await bot.get_me()
#             # evbots.init_bot(bot, bot_user.username) # добавляешь в БД
#             await message.answer(f"New bot started: @{bot_user.username}")
#         except (TokenValidationError, TelegramUnauthorizedError) as err:
#             await message.answer(fmt.quote(f"{type(err).__name__}: {str(err)}"))
#     else:
#         await message.answer("Please provide token")


# @router.message(Command("stopbot"))
# async def cmd_start(message: types.Message, command: CommandObject, polling_manager: PollingManager,):

#     if command.args:
#         try:
#             polling_manager.stop_bot_polling(int(command.args))
#             # evbots.delete_bot(int(command.args)) # удаляешь из бд
#             await message.answer("Bot stopped")
#         except (ValueError, KeyError) as err:
#             await message.answer(fmt.quote(f"{type(err).__name__}: {str(err)}"))
#     else:
#         await message.answer("Please provide bot id")


# @router.post('/bot/toggle_lang')
# async def receive_bot_name(request: Request, state: FSMContext):
#     try:
#         data = await request.json()
#         value, user_id = data.get('value'), data.get('user_id')

#         if not user_id:
#             raise HTTPException(status_code=401, detail='Authorization error')

#         # Обновление состояния FSM
#         await state.update_data(lang=value)

#         # Пример вызова user_update (раскомментируйте и адаптируйте под свою логику)
#         # result = await rq.user_update_bot(user_id, api, 'status', value=='on')
#         result = {"message": "Language updated successfully", "lang": value}

#         return JSONResponse(content=result, headers=CORS_HEADERS)
#     except Exception as error:
#         logger.error(f'Ошибка при обработке запроса от {user_id}: {error}')
#         raise HTTPException(status_code=500, detail='Internal server error')
