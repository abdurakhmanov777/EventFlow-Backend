import sys
import os

# Настройка пути к корню проекта
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.insert(0, BASE_DIR)

import pytest, difflib
from app.utils.morphology import inflect_text
from tests.test_cases import test_cases

pytest_plugins = 'pytest_asyncio'



def get_diff(expected: str, actual: str) -> str:
    diff = difflib.ndiff([expected], [actual])
    return '\n'.join(diff)


@pytest.mark.asyncio
@pytest.mark.parametrize('text, case, expected', test_cases)
async def test_inflect_text(text: str, case: str, expected: str):
    result = await inflect_text(text, case)
    assert result == expected, (
        f'\n[❌] Тест провален\n'
        f'────────────────────────────\n'
        f'  Входной текст: {text}\n'
        f'  Падеж:         {case}\n'
        f'  Ожидалось:     {expected}\n'
        f'  Получено:      {result}\n'
        f'────────────────────────────\n'
        f'  Разница:\n{get_diff(expected, result)}'
    )
