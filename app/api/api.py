from fastapi import APIRouter, BackgroundTasks, Request, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
from fastapi import Depends

from app.modules.multibot import start_bot, stop_bot
from app.modules.polling_manager import PollingManager
import app.database.requests as rq

from app.modules.polling_manager import get_polling_manager

router = APIRouter()

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


@router.post('/bot/delete_bot')
async def delete_bot(
    request: Request,
    background_tasks: BackgroundTasks,
    polling_manager: PollingManager = Depends(get_polling_manager)
):
    try:
        data = await request.json()
        name = data.get('name')
        user_id = data.get('user_id')

        if not user_id:
            raise HTTPException(status_code=401, detail='Authorization error')
        if not name:
            raise HTTPException(status_code=400, detail='Incorrect data')

        bot_api, bot_on, result = await rq.delete_bot(user_id, name)

        if bot_api and bot_on:
            background_tasks.add_task(stop_bot, bot_api, polling_manager)

        return JSONResponse(content=result, headers=CORS_HEADERS)

    except Exception as error:
        logger.error(f'Ошибка при обработке запроса от {data.get('user_id', 'неизвестен')}: {error}')
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
async def toggle_bot(
    request: Request,
    background_tasks: BackgroundTasks,
    polling_manager: PollingManager = Depends(get_polling_manager)
):
    try:
        data = await request.json()
        value = data.get('value')
        api = data.get('api')
        user_id = data.get('user_id')

        if not user_id:
            logger.warning('Отсутствует user_id')
            raise HTTPException(status_code=401, detail='Authorization error')

        result = await rq.user_update_bot(user_id, api, 'status', value == 'on')

        # Запуск действия в фоне, не блокируя ответ клиенту
        if value == 'on':
            background_tasks.add_task(start_bot, api, polling_manager)
        else:
            background_tasks.add_task(stop_bot, api, polling_manager)

        return JSONResponse(content=result, headers=CORS_HEADERS)

    except Exception as error:
        logger.error(f'Ошибка обработки запроса: {error}')
        raise HTTPException(status_code=500, detail='Internal server error')
