import re
import pymorphy3

# Создаем экземпляр морфологического анализатора
morph = pymorphy3.MorphAnalyzer()

FIX_O_PATTERN = re.compile(r"\b([оО])\s+([«'“‘(]*)(\w)")
VOWELS = set('аеёиоуыэюяАЕЁИОУЫЭЮЯ')

SENTENCE_ENDINGS_PATTERN = re.compile(r'([.!?])(\s+|$)')
WORD_PATTERN = re.compile(r'\w+|\s+|[^\w\s]', re.UNICODE)


async def process_text(
    text: str, case: str, first: bool = False, fix_o: str = None
) -> str:
    text = await inflect_text(text, case)
    text = await lowercase_except_abbreviations(text, first)

    if fix_o:
        text = await fix_preposition_o(fix_o + text)

    return text



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

    # Поиск первого существительного (обрабатываем только одно раз)
    noun = next((p for p in parsed if 'NOUN' in p.tag), None)
    if not noun:
        return text

    # Получение числа (ед. или мн. число)
    number = noun.tag.number
    result = []

    # Обработка каждого слова
    for word, parse in zip(words, parsed):
        if (
            parse == noun or
            ('ADJF' in parse.tag and parse.tag.number == number)
        ):
            tags = set()

            # Особая логика для винительного падежа
            if case_code == 'accs':
                if 'NOUN' in parse.tag:
                    if parse.tag.gender == 'femn' and parse.tag.number == 'sing':
                        tags.add('accs')
                    elif 'anim' in parse.tag:
                        tags.add('accs')
                    else:
                        tags.add('nomn')
                elif 'ADJF' in parse.tag:
                    if parse.tag.gender == 'femn' and parse.tag.number == 'sing':
                        tags.add('accs')
                    elif 'anim' in noun.tag:
                        tags.add('accs')
                    else:
                        tags.add('nomn')
            else:
                tags.add(case_code)

            # Добавление числа (если известно)
            if number:
                tags.add(number)

            # Склонение и добавление слова
            inflected = parse.inflect(tags)
            new_word = inflected.word if inflected else word
            result.append(preserve_case(word, new_word))
        else:
            result.append(word)

    # Возвращаем результат
    return ' '.join(result)



async def fix_preposition_o(text: str) -> str:
    '''
    Заменяет предлог о/О на об/Об перед словами, начинающимися на гласную букву.
    '''
    def replacer(match):
        preposition, prefix, first_letter = match.groups()
        if first_letter in VOWELS:
            return f'{"Об" if preposition == "О" else "об"} {prefix}{first_letter}'
        return match.group(0)

    return FIX_O_PATTERN.sub(replacer, text)


async def lowercase_except_abbreviations(text: str, capitalize_first: bool = True) -> str:
    def is_abbreviation(word: str) -> bool:
        return word.isupper() and len(word) > 1

    def process_word(word: str) -> str:
        return word if is_abbreviation(word) else word.lower()

    # Разделение текста на предложения с сохранением пунктуации
    parts = SENTENCE_ENDINGS_PATTERN.split(text)
    sentences = ["".join(parts[i:i+2]) for i in range(0, len(parts), 2)]

    processed_sentences = []
    for sentence in sentences:
        tokens = WORD_PATTERN.findall(sentence)
        result = []
        capitalize_next = capitalize_first

        for token in tokens:
            if token.strip() and token.isalpha():  # Слово
                word = process_word(token)
                if capitalize_next and not is_abbreviation(word):
                    word = word.capitalize()
                result.append(word)
                capitalize_next = False
            else:
                result.append(token)
                if token in '.!?':  # Пунктуация
                    capitalize_next = capitalize_first

        processed_sentences.append(''.join(result))

    return ''.join(processed_sentences)
