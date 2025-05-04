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

async def inflect_text(text: str, case: str) -> str:
    '''
    Изменяет падеж словосочетания/слова с именительного на выбранный,
    сохраняя регистр каждой буквы. Учитывает число и корректный морфоанализ.
    '''
    # Получаем код падежа по его строковому названию
    case_code = CASES.get(case)
    if not case_code:
        return f'Неизвестный падеж: {case}'

    # Выбирает наиболее подходящий разбор слова:
    # в приоритете существительные и прилагательные в именительном падеже
    def choose_best_parse(word):
        parses = morph.parse(word)
        for p in parses:
            if 'NOUN' in p.tag and 'nomn' in p.tag:
                return p
            if 'ADJF' in p.tag and 'nomn' in p.tag:
                return p
        return parses[0]  # Если ничего не найдено — берем первый разбор

    words = text.split()  # Разбиваем фразу на отдельные слова
    parsed = [choose_best_parse(word) for word in words]  # Морфологический разбор каждого слова

    # Ищем индекс первого существительного (якоря согласования по числу)
    noun_index = next((i for i, p in enumerate(parsed) if 'NOUN' in p.tag), -1)
    if noun_index == -1:
        return text  # Если нет существительного — возвращаем оригинальный текст

    noun_number = parsed[noun_index].tag.number  # Определяем число (ед. или мн.) существительного
    result = []

    # Функция для сохранения регистра букв (верхний/нижний) при замене слова
    def preserve_letter_case(original: str, new: str) -> str:
        res = []
        for o, n in zip(original, new):
            res.append(n.upper() if o.isupper() else n.lower())  # Сохраняем регистр символов
        if len(new) > len(original):  # Добавляем оставшиеся символы, если новое слово длиннее
            res.extend(new[len(original):])
        return ''.join(res)

    for i, (word, p) in enumerate(zip(words, parsed)):
        # Решаем, нужно ли изменять это слово:
        # изменяем существительное и прилагательные с тем же числом
        should_inflect = (
            i == noun_index or
            ('ADJF' in p.tag and p.tag.number == noun_number)
        )

        if should_inflect:
            tags_to_inflect = {case_code}  # Тег нужного падежа
            if noun_number:
                tags_to_inflect.add(noun_number)  # Добавляем тег числа (если есть)

            inflected = p.inflect(tags_to_inflect)  # Пробуем склонить слово
            new_word = inflected.word if inflected else word  # Если не получилось — оставляем как есть
            result.append(preserve_letter_case(word, new_word))  # Сохраняем регистр
        else:
            result.append(word)  # Оставляем слово без изменений

    return ' '.join(result)  # Собираем и возвращаем итоговую строку




async def fix_preposition_o(text: str) -> str:
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
