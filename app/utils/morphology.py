import pymorphy3
import re

# Создаем экземпляр морфологического анализатора
morph = pymorphy3.MorphAnalyzer()

# Сопоставление падежей с кодами pymorphy3
CASES = {
    'именительный': 'nomn',
    'родительный': 'gent',
    'дательный': 'datv',
    'винительный': 'accs',
    'творительный': 'ablt',
    'предложный': 'loct'
}

def inflect_text(text: str, case: str) -> str:
    '''
    Изменяет падеж словосочетания/слова с именительного на выбранный,
    сохраняя регистр каждой буквы.
    '''
    case_code = CASES.get(case)
    if not case_code:
        return f'Неизвестный падеж: {case}'

    words = text.split()  # Разбиваем фразу на слова
    parsed = [morph.parse(word)[0] for word in words]  # Разбираем каждое слово

    # Находим индекс первого существительного
    noun_index = next((i for i, p in enumerate(parsed) if 'NOUN' in p.tag), -1)
    if noun_index == -1:
        return text  # Если нет существительного — возвращаем исходный текст

    noun_gender = parsed[noun_index].tag.gender  # Определяем род существительного
    result = []

    def preserve_letter_case(original: str, new: str) -> str:
        '''
        Сохраняет регистр букв из оригинального слова в новом.
        '''
        res = []
        for o, n in zip(original, new):
            res.append(n.upper() if o.isupper() else n.lower())
        # Добавляем символы, если новое слово длиннее
        if len(new) > len(original):
            res.extend(new[len(original):])
        return ''.join(res)

    for i, (word, p) in enumerate(zip(words, parsed)):
        # Склоняем существительное и прилагательные, согласованные по роду
        should_inflect = (
            i == noun_index or
            ('ADJF' in p.tag and p.tag.gender == noun_gender)
        )

        if should_inflect:
            inflected = p.inflect({case_code})  # Пытаемся склонить
            new_word = inflected.word if inflected else word  # Если не получилось — оставляем как есть
            result.append(preserve_letter_case(word, new_word))
        else:
            result.append(word)  # Остальные слова не изменяются

    return ' '.join(result)  # Собираем результат обратно в строку


def fix_preposition_o(text: str) -> str:
    '''
    Заменяет предлог "о" на "об" перед словами, начинающимися на гласную букву.
    '''
    def replacer(match):
        prefix, first_letter = match.groups()
        # Если первая буква после "о" — гласная, используем "об"
        preposition = 'об' if first_letter in 'аеёиоуыэюяАЕЁИОУЫЭЮЯ' else 'о'
        return f'{preposition} {prefix}{first_letter}'

    # Шаблон: "о" + пробел + опциональные кавычки/скобки + первая буква слова
    pattern = r"\bо\s+([«'“‘(]*)(\w)"
    return re.sub(pattern, replacer, text)  # Заменяем все подходящие случаи
