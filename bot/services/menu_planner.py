"""Меню на день/тиждень: кандидати з БД → LLM розставляє ID по слотах."""

from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import repo
from bot.db.models import Recipe
from bot.services.llm.base import LLMClient, MenuPlanResult, QueryIntent
from bot.services.retrieval import compact, gather_candidates

MEALS_BY_COUNT = {1: ["dinner"], 2: ["lunch", "dinner"], 3: ["breakfast", "lunch", "dinner"]}


async def plan_menu(
    session: AsyncSession,
    llm: LLMClient,
    group_id: int,
    user_query: str,
    intent: QueryIntent,
) -> tuple[MenuPlanResult, dict[int, Recipe]]:
    days = min(intent.days or 1, 7)
    meals_per_day = intent.meals_per_day or 3

    # Для меню беремо всю базу групи (фільтр лише за інгредієнтами/складністю),
    # правило неповторення застосовуємо як і для окремих страв.
    menu_intent = intent.model_copy(update={"meal_types": []})
    candidates = await gather_candidates(session, group_id, menu_intent)
    if not candidates:
        return MenuPlanResult(comment="У базі поки немає рецептів для меню."), {}

    result = await llm.plan_menu(
        user_query,
        compact(candidates),
        days=days,
        meals_per_day=meals_per_day,
        max_calories_per_day=intent.max_calories_per_day,
    )
    by_id = {r.id: r for r in candidates}

    # Захист від галюцинацій: лишаємо тільки реальні ID, без повторів у межах меню
    used: set[int] = set()
    valid_slots = []
    for slot in result.slots:
        if slot.recipe_id in by_id and slot.recipe_id not in used and 1 <= slot.day <= days:
            valid_slots.append(slot)
            used.add(slot.recipe_id)
    result.slots = valid_slots
    return result, by_id


async def replace_slot(
    session: AsyncSession,
    llm: LLMClient,
    group_id: int,
    user_query: str,
    intent: QueryIntent,
    current_plan: list[dict],
) -> tuple[int | None, dict[int, Recipe]]:
    """Замінює одну позицію меню. Повертає новий recipe_id (або None) і кандидатів."""
    used_ids = {slot["recipe_id"] for slot in current_plan}
    meal = intent.replace_meal or "dinner"
    slot_intent = intent.model_copy(
        update={"meal_types": [meal], "specific_dish": None}
    )
    candidates = await gather_candidates(
        session, group_id, slot_intent, exclude_ids=used_ids
    )
    if not candidates:
        return None, {}
    selection = await llm.select_recipes(
        f"Підбери іншу страву на {meal} замість поточної. Побажання: {user_query}",
        compact(candidates),
    )
    by_id = {r.id: r for r in candidates}
    valid = [i for i in selection.selected_ids if i in by_id]
    return (valid[0] if valid else candidates[0].id), by_id
