"""render_served_list: рекомендовані за категоріями, суфікс (прийом їжі, дата)."""

from datetime import date

from bot.db.models import Recipe, RecipeCategory, ServeHistory
from bot.rendering import render_served_list


def pair(recipe_id, title, cats=(), meal_type=None, served_on=None):
    recipe = Recipe(
        id=recipe_id,
        title=title,
        categories=[RecipeCategory(category=c) for c in cats],
    )
    sh = ServeHistory(
        recipe_id=recipe_id,
        meal_type=meal_type,
        served_on=served_on or date(2026, 7, 12),
    )
    return sh, recipe


def test_sections_follow_categories_order():
    text = render_served_list(
        [
            pair(1, "Плов", ["dinner"]),
            pair(2, "Сирники", ["breakfast"]),
        ]
    )
    assert text.startswith("🕐 <b>Останні рекомендовані страви:</b>")
    assert text.index("🍳 Сніданок") < text.index("🌙 Вечеря")


def test_meal_and_date_suffix():
    text = render_served_list([pair(1, "Борщ", ["lunch"], meal_type="lunch")])
    assert "Борщ (Обід, 12.07)" in text


def test_date_only_when_meal_unknown():
    text = render_served_list([pair(1, "Борщ", ["lunch"], meal_type="tea")])
    assert "Борщ (12.07)" in text


def test_no_category_falls_into_general_with_sequential_numbers():
    text = render_served_list(
        [
            pair(7, "Плов"),
            pair(8, "Сирники", ["breakfast"]),
        ]
    )
    assert "🍽 Загальна" in text
    assert "1. Сирники" in text  # сніданок іде першим у порядку CATEGORIES
    assert "2. Плов" in text
