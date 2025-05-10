import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_URL = os.getenv('DB_URL')
LOG_FILE = os.getenv('LOG_FILE')
FASTAPI_LOG_FILE = os.getenv('FASTAPI_LOG_FILE')
LOCALIZATION_LANGUAGE = os.getenv('LOCALIZATION_LANGUAGE')
TIME_ZONE = int(os.getenv('TIME_ZONE'))
MAIN_ADMINS = list(map(int, os.getenv('MAIN_ADMINS', '').split(','))) if os.getenv('MAIN_ADMINS') else []
