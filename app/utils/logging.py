import sys
import traceback
from pathlib import Path
from loguru import logger

async def log(event, error=None, info=None):
    user_id = event.from_user.id
    username = event.from_user.username
    frame = sys._getframe(1)
    func_name = frame.f_code.co_name
    filename = Path(frame.f_code.co_filename).name

    if error:
        tb = traceback.extract_tb(error.__traceback__)[-1]
        message = f"{func_name} [{filename}:{tb.lineno}] ERROR: {error} ({user_id}, {username})"
        logger.error(message)
    else:
        message = f"{func_name} [{filename}:{frame.f_lineno}] {f'({info}) ' if info else ''}({user_id}, {username})"
        logger.info(message)
