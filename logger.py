from http import HTTPStatus
from loguru import logger
from config import LOG_FILE
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time

logger.add(sink=LOG_FILE, format='{time} {level} {message}')

def get_status_phrase(code: int) -> str:
    return HTTPStatus(code).phrase if code in HTTPStatus._value2member_map_ else 'Unknown'

class LoguruLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = round(time.perf_counter() - start, 4)

        logger.info(
            f'{request.method} {request.url.path} {response.status_code} '
            f'{get_status_phrase(response.status_code)} {duration}s'
        )
        return response
