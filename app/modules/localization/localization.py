import json
import os

from loguru import logger

class Localization:
    def __init__(self, localization_data: dict):
        self._parse_data(localization_data)

    def _parse_data(self, data: dict):
        for key, value in data.items():
            # Если значение — это словарь, рекурсивно преобразуем его
            if isinstance(value, dict):
                # Создаем атрибут для текущего ключа, если это словарь
                setattr(self, key, Localization(value))  # Рекурсивное создание атрибута
            else:
                setattr(self, key, value)



async def load_localization_main(language: str) -> Localization:
    localization_file_path = 'app/modules/localization/main/'
    localization_file_name = language + '.json'

    try:
        # Загружаем данные из файла локализации
        with open(os.path.join(localization_file_path, localization_file_name), mode='r', encoding='utf8') as localization_file:
            localization_dict = json.load(localization_file)
            return Localization(localization_dict)
    except Exception as error:
        logger.error(f'Error loading localization file: {error}')
        return Localization({})


async def load_localization_multibot(language: str) -> Localization:
    localization_file_path = 'app/modules/localization/multibot/'
    localization_file_name = language + '.json'

    try:
        # Загружаем данные из файла локализации
        with open(os.path.join(localization_file_path, localization_file_name), mode='r', encoding='utf8') as localization_file:
            localization_dict = json.load(localization_file)
            return Localization(localization_dict)
    except Exception as error:
        logger.error(f'Error loading localization file: {error}')
        return Localization({})
