import inspect
import traceback
from loguru import logger


def log(user_id, username, error=None, info=None):
    frame = inspect.currentframe().f_back
    func = frame.f_code

    # Обрезаем путь до "app"
    def shorten(path):
        return path[path.find('app'):] if 'app' in path else path

    filename = shorten(func.co_filename)

    # Если ошибка передана, получаем ее точное местоположение
    if error:
        tb = traceback.extract_tb(error.__traceback__)[-1]
        log_message = f'{func.co_name} [{filename}:{tb.lineno}] ERROR: {error} ({user_id}, {username})'
    else:
        lineno = frame.f_lineno
        log_message = f'{func.co_name} [{filename}:{lineno}] {f"({info}) " if info else ""}({user_id}, {username})'

    (logger.error if error else logger.info)(log_message)
