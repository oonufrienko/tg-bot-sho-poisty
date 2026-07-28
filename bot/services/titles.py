"""Єдиний стиль назв рецептів.

LLM переносить назву дослівно, тож зі скріна з КАПСОМ приходить «СИРНИКИ»,
а зі звичайного фото — «Сирники». Тут це вирівнюється детерміновано, без LLM.
"""

import re

# Власні назви беруть у лапки («Цезар») — їхню першу літеру теж лишаємо великою.
_QUOTED = re.compile(r'«[^»]*»|„[^“”]*[“”]|“[^”]*”|"[^"]*"')


_OPENING_QUOTES = '«„“"'


def _capitalize_first(text: str) -> str:
    """Велика перша літера. Лапки перед нею пропускаємо, решту — ні:
    «5 хвилин на сніданок» лишається з малої, як звичайне речення.
    """
    index = 0
    while index < len(text) and text[index] in _OPENING_QUOTES:
        index += 1
    if index >= len(text) or not text[index].isalpha():
        return text
    return text[:index] + text[index].upper() + text[index + 1 :]


def _is_shouting(text: str) -> bool:
    """Назва «кричить», якщо літер кілька і жодна з них не мала."""
    letters = [char for char in text if char.isalpha()]
    return len(letters) >= 2 and not any(char.islower() for char in letters)


def _unshout(text: str) -> str:
    parts: list[str] = []
    last = 0
    for match in _QUOTED.finditer(text):
        parts.append(text[last : match.start()].lower())
        parts.append(_capitalize_first(match.group().lower()))
        last = match.end()
    parts.append(text[last:].lower())
    return "".join(parts)


def normalize_title(title: str) -> str:
    """Назва з великої літери; КАПС розкапслюється, назви в лапках — лишаються.

    Якщо в назві вже є малі літери, регістр не чіпаємо взагалі: «Паста
    Карбонара» і «ПП-млинці» лишаються як є. Власна назва без лапок у
    КАПС-заголовку велику літеру втратить («ТОРТ НАПОЛЕОН» → «Торт наполеон») —
    відрізнити її від звичайного слова без LLM неможливо.
    """
    cleaned = " ".join(title.split())
    if not cleaned:
        return cleaned
    if _is_shouting(cleaned):
        cleaned = _unshout(cleaned)
    return _capitalize_first(cleaned)
