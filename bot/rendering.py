"""Формування текстів відповідей. Рецепти рендеряться ДОСЛІВНО з БД."""

from html import escape

from bot.db.models import CATEGORIES, MEAL_LABELS, Recipe


def _ingredient_line(item: dict) -> str:
    name = escape((item.get("name") or "").strip())
    qty = escape((item.get("qty") or "").strip())
    unit = escape((item.get("unit") or "").strip())
    amount = " ".join(part for part in (qty, unit) if part)
    return f"• {name} — {amount}" if amount else f"• {name}"


def render_recipe(recipe: Recipe, full: bool = True) -> str:
    lines = [f"🍽 <b>{escape(recipe.title)}</b>"]

    meta = []
    if recipe.category_keys:
        meta.append(
            " ".join(CATEGORIES.get(c, c) for c in recipe.category_keys)
        )
    if recipe.difficulty:
        meta.append("складність: " + "⭐" * recipe.difficulty)
    if recipe.calories:
        meta.append(f"{recipe.calories} ккал")
    if meta:
        lines.append(" | ".join(meta))

    if recipe.ingredients:
        lines.append("\n<b>Інгредієнти:</b>")
        lines.extend(_ingredient_line(item) for item in recipe.ingredients)

    if full and recipe.steps:
        lines.append("\n<b>Як готувати:</b>")
        lines.append(escape(recipe.steps))

    return "\n".join(lines)


def render_menu_day(day: int, slots: list[dict], recipes: dict[int, Recipe]) -> str:
    lines = [f"📅 <b>День {day}</b>"]
    for slot in slots:
        recipe = recipes.get(slot["recipe_id"])
        if recipe is None:
            continue
        meal = MEAL_LABELS.get(slot["meal"], slot["meal"])
        lines.append(f"\n<u>{meal}</u>")
        lines.append(render_recipe(recipe))
    return "\n".join(lines)


def render_shopping_list(lines: list[str], days: int) -> str:
    period = "день" if days == 1 else f"{days} дн."
    header = f"🛒 <b>Список покупок ({period})</b>\n"
    body = "\n".join(f"☐ {escape(line)}" for line in lines)
    footer = "\n\nПерешліть це повідомлення тому, хто йде в магазин 😉"
    return header + body + footer


def render_extraction_card(
    title: str | None,
    ingredients: list[dict],
    steps: str | None,
    calories: int | None,
    missing_info: list[str],
) -> str:
    lines = ["📝 <b>Ось що я розпізнав:</b>\n"]
    lines.append(f"<b>{escape(title)}</b>" if title else "<i>Назву не розпізнано</i>")
    if ingredients:
        lines.append("\n<b>Інгредієнти:</b>")
        lines.extend(_ingredient_line(item) for item in ingredients)
    else:
        lines.append("\n<i>Інгредієнти не розпізнано</i>")
    if steps:
        preview = steps if len(steps) <= 700 else steps[:700] + "…"
        lines.append("\n<b>Як готувати:</b>")
        lines.append(escape(preview))
    else:
        lines.append("\n<i>Кроки приготування не розпізнано</i>")
    if calories:
        lines.append(f"\nКалорії: {calories} ккал")
    if missing_info:
        lines.append("\n⚠️ <b>Потрібне уточнення:</b>")
        lines.extend(f"— {escape(question)}" for question in missing_info)
        lines.append("\nНатисніть «✏️ Доповнити» і надішліть відповідь текстом.")
    lines.append("\nОберіть категорії та складність, потім «✅ Зберегти».")
    return "\n".join(lines)
