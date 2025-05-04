from http import HTTPStatus
from loguru import logger
from config import LOG_FILE
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time


def get_status_phrase(status_code: int) -> str:
    '''Получаем фразу статуса из HTTPStatus, возвращаем 'Unknown' в случае ошибки'''
    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return 'Unknown'


# Настройка Loguru
logger.add(
    sink=LOG_FILE,
    format='{time} {level} {message}'
)


class LoguruLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Начало измерения времени
        start_time = time.time()

        # Получаем ответ после обработки запроса
        response = await call_next(request)

        # Время выполнения запроса
        duration = round(time.time() - start_time, 4)

        # Получаем фразу статуса из маппинга или 'Unknown' для неизвестных кодов
        status_phrase = get_status_phrase(response.status_code)

        # Формируем сообщение для логирования
        log_message = (
            f"'{request.method} {request.url.path}' "
            f"{response.status_code} {status_phrase} "
            f'{duration}s'
        )

        # Логирование с уровнем INFO
        logger.info(log_message)

        return response
