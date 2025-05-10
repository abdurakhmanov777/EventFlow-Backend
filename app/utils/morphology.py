import re, pymorphy3

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
    # Получение кода падежа
    case_code = CASES.get(case)
    if not case_code:
        return f'Неизвестный падеж: {case}'

    # Функция для выбора лучшего разбора слова
    def choose_best_parse(word):
        parses = morph.parse(word)
        for p in parses:
            if 'NOUN' in p.tag and 'nomn' in p.tag:
                return p
            if 'ADJF' in p.tag and 'nomn' in p.tag:
                return p
        return parses[0]

    # Функция для сохранения регистра исходного слова
    def preserve_case(original, new):
        return ''.join(
            n.upper() if o.isupper() else n.lower()
            for o, n in zip(original, new)
        ) + new[len(original):]

    # Разбиение текста на слова и их разбор
    words = text.split()
    parsed = [choose_best_parse(w) for w in words]

    # Поиск существительного в тексте
    noun = next((p for p in parsed if 'NOUN' in p.tag), None)
    if not noun:
        return text

    # Получение числа существительного (ед. или мн. число)
    number = noun.tag.number
    result = []

    # Обработка каждого слова в тексте
    for word, parse in zip(words, parsed):
        if parse == noun or ('ADJF' in parse.tag and parse.tag.number == number):
            tags = set()

            # Применение падежа для существительных и прилагательных
            if case_code == 'accs':
                if 'NOUN' in parse.tag:
                    if parse.tag.gender == 'femn' and parse.tag.number == 'sing':
                        tags.add('accs')
                    elif 'anim' in parse.tag:
                        tags.add('accs')  # Для одушевлённых существительных
                    else:
                        tags.add('nomn')
                elif 'ADJF' in parse.tag:
                    if parse.tag.gender == 'femn' and parse.tag.number == 'sing':
                        tags.add('accs')
                    elif 'anim' in noun.tag:
                        tags.add('accs')  # Для одушевлённых прилагательных
                    else:
                        tags.add('nomn')
            else:
                tags.add(case_code)

            # Учет числа (единственное или множественное)
            if number:
                tags.add(number)

            # Применение склонения
            inflected = parse.inflect(tags)
            new_word = inflected.word if inflected else word
            result.append(preserve_case(word, new_word))
        else:
            result.append(word)

    # Собираем результат
    return ' '.join(result)




async def fix_preposition_o(text: str) -> str:
    '''
    Заменяет предлог о/О на об/Об перед словами, начинающимися на гласную букву.
    '''
    def replacer(match):
        preposition = match.group(1)
        prefix = match.group(2)
        first_letter = match.group(3)
        is_upper = preposition[0].isupper()

        # Выбираем правильную форму предлога
        replacement = 'Об' if is_upper else 'об' if first_letter in 'аеёиоуыэюяАЕЁИОУЫЭЮЯ' else preposition
        return f'{replacement} {prefix}{first_letter}'

    # Шаблон: о/О + пробел + опциональные кавычки/скобки + первая буква
    pattern = r"\b([оО])\s+([«'“‘(]*)(\w)"
    return re.sub(pattern, replacer, text)
