"""render_served_list: групування за датами, свіжа дата зверху."""

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


def test_groups_by_date_latest_first():
    text = render_served_list(
        [
            pair(1, "Салат", served_on=date(2026, 7, 16)),
            pair(2, "Сирники", meal_type="breakfast", served_on=date(2026, 7, 17)),
        ]
    )
    assert text.startswith("🕐 <b>Останні рекомендовані страви:</b>")
    assert text.index("<b>17.07</b>") < text.index("<b>16.07</b>")
    # рядок дня — «Прийом: Назва», без нумерації
    assert "Сніданок: Сирники" in text
    assert "Загальна: Салат" in text


def test_meals_ordered_within_a_day():
    day = date(2026, 7, 17)
    text = render_served_list(
        [
            pair(1, "Плов", meal_type="dinner", served_on=day),
            pair(2, "Борщ", meal_type="lunch", served_on=day),
            pair(3, "Сирники", meal_type="breakfast", served_on=day),
        ]
    )
    assert text.count("<b>17.07</b>") == 1
    assert (
        text.index("Сніданок: Сирники")
        < text.index("Обід: Борщ")
        < text.index("Вечеря: Плов")
    )


def test_unknown_meal_goes_last_as_general():
    day = date(2026, 7, 17)
    text = render_served_list(
        [
            pair(1, "Чай", meal_type="tea", served_on=day),
            pair(2, "Плов", meal_type="dinner", served_on=day),
        ]
    )
    # невідомий прийом їжі падає в «Загальна» і йде після відомих
    assert text.index("Вечеря: Плов") < text.index("Загальна: Чай")
