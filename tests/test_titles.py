"""normalize_title: КАПС розкапслюється, власні назви в лапках лишаються."""

import pytest

from bot.services.llm.base import RecipeExtraction
from bot.services.titles import normalize_title


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("СИРНИКИ З ІЗЮМОМ", "Сирники з ізюмом"),
        ('САЛАТ "ЦЕЗАРЬ"', 'Салат "Цезарь"'),
        ("САЛАТ «ЦЕЗАР» З КУРКОЮ", "Салат «Цезар» з куркою"),
        ("CAESAR SALAD", "Caesar salad"),
        ("сирники з ізюмом", "Сирники з ізюмом"),
        # Є малі літери — регістр не чіпаємо взагалі.
        ("Салат «Цезар»", "Салат «Цезар»"),
        ("Паста Карбонара", "Паста Карбонара"),
        ("ПП-млинці", "ПП-млинці"),
        ("  Борщ   зелений ", "Борщ зелений"),
        ("", ""),
        ("   ", ""),
        # Не літера на початку — велика стає перша ж літера.
        ("5 ХВИЛИН НА СНІДАНОК", "5 хвилин на сніданок"),
    ],
)
def test_normalize_title(raw, expected):
    assert normalize_title(raw) == expected


def test_normalization_is_idempotent():
    once = normalize_title("СИРНИКИ З «ІЗЮМОМ»")
    assert normalize_title(once) == once


def test_extraction_normalizes_title():
    """Валідатор у схемі — щоб картка показувала те саме, що піде в базу."""
    assert RecipeExtraction(is_recipe=True, title="СИРНИКИ").title == "Сирники"
    assert RecipeExtraction(is_recipe=True).title is None
