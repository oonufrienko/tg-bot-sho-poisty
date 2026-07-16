"""render_recipe_list: групування за категоріями та наскрізна нумерація."""

import re

from bot.db.models import Recipe, RecipeCategory
from bot.rendering import render_recipe_list


def make(recipe_id, title, cats=(), difficulty=None):
    return Recipe(
        id=recipe_id,
        title=title,
        difficulty=difficulty,
        categories=[RecipeCategory(category=c) for c in cats],
    )


def test_sections_follow_categories_order_and_empty_sections_absent():
    recipes = [
        make(1, "Плов", ["dinner"]),
        make(2, "Сирники", ["breakfast"]),
        make(3, "Наполеон", ["dessert"]),
    ]
    text, _ = render_recipe_list(recipes)
    assert text.index("🍳 Сніданок") < text.index("🌙 Вечеря") < text.index("🍰 Десерт")
    assert "🍲 Обід" not in text
    assert "🥗 Салати" not in text


def test_multi_category_recipe_shown_once_under_first_category():
    text, ids = render_recipe_list([make(1, "Сирники", ["dessert", "breakfast"])])
    assert text.count("Сирники") == 1
    assert "🍰 Десерт" in text
    assert "🍳 Сніданок" not in text
    assert ids == [1]


def test_no_category_and_unknown_category_fall_into_general():
    text, _ = render_recipe_list(
        [make(1, "Плов"), make(2, "Щось дивне", ["weird"])]
    )
    assert "🍽 Загальна" in text
    assert text.index("🍽 Загальна") < text.index("Плов")
    assert text.index("🍽 Загальна") < text.index("Щось дивне")


def test_numbering_is_sequential_and_matches_ids():
    recipes = [
        make(11, "Плов"),  # general — піде останнім
        make(22, "Сирники", ["breakfast"]),
        make(33, "Борщ", ["lunch"]),
    ]
    text, ids = render_recipe_list(recipes)
    # Номер i у тексті має вказувати на ids[i-1] — на цьому тримається
    # видалення/редагування за номером.
    numbered = dict(re.findall(r"^(\d+)\. (\S+)", text, flags=re.MULTILINE))
    assert numbered == {"1": "Сирники", "2": "Борщ", "3": "Плов"}
    assert ids == [22, 33, 11]


def test_difficulty_rendered_as_stars():
    text, _ = render_recipe_list(
        [make(1, "Борщ", ["lunch"], difficulty=3), make(2, "Плов")]
    )
    assert "Борщ ⭐⭐⭐" in text
    assert "Плов ⭐" not in text
    assert text.count("Плов") == 1


def test_title_is_html_escaped():
    text, _ = render_recipe_list([make(1, "Борщ <b>жирний</b>")])
    assert "&lt;b&gt;жирний&lt;/b&gt;" in text
    assert "<b>жирний</b>" not in text
