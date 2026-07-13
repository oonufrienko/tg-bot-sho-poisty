"""Підбір страв: код дістає кандидатів з БД, LLM лише обирає ID з них."""

from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import repo
from bot.db.models import Recipe
from bot.services.llm.base import LLMClient, QueryIntent, SelectionResult

MAX_CANDIDATES = 60


def compact(recipes: list[Recipe]) -> list[dict]:
    """Компактне подання рецептів для промпта (без повного тексту кроків)."""
    return [
        {
            "id": r.id,
            "title": r.title,
            "categories": r.category_keys,
            "ingredients": [i.get("name") for i in r.ingredients],
            "calories": r.calories,
            "difficulty": r.difficulty,
        }
        for r in recipes
    ]


def _matches_ingredients(recipe: Recipe, intent: QueryIntent) -> bool:
    names = " ".join((i.get("name") or "").lower() for i in recipe.ingredients)
    haystack = f"{recipe.title.lower()} {names}"
    for excluded in intent.exclude_ingredients:
        if excluded.lower() in haystack:
            return False
    for included in intent.include_ingredients:
        if included.lower() not in haystack:
            return False
    return True


async def gather_candidates(
    session: AsyncSession,
    group_id: int,
    intent: QueryIntent,
    exclude_ids: set[int] = frozenset(),
    apply_no_repeat: bool = True,
) -> list[Recipe]:
    categories = intent.meal_types or None
    recipes = await repo.group_recipes(session, group_id, categories)
    # Якщо за категоріями нічого немає — шукаємо по всій базі групи
    if not recipes and categories:
        recipes = await repo.group_recipes(session, group_id)

    # Правило неповторення: страва не частіше 1 разу на тиждень,
    # окрім випадку, коли користувач попросив конкретну страву.
    skip: set[int] = set(exclude_ids)
    if apply_no_repeat and not intent.specific_dish:
        skip |= await repo.recently_served_ids(session, group_id, days=7)

    result = []
    for recipe in recipes:
        if recipe.id in skip:
            continue
        if intent.max_difficulty and (recipe.difficulty or 0) > intent.max_difficulty:
            continue
        if not _matches_ingredients(recipe, intent):
            continue
        result.append(recipe)
    return result[:MAX_CANDIDATES]


async def find_dish(
    session: AsyncSession,
    llm: LLMClient,
    group_id: int,
    user_query: str,
    intent: QueryIntent,
    exclude_ids: set[int] = frozenset(),
) -> tuple[SelectionResult, dict[int, Recipe]]:
    candidates = await gather_candidates(session, group_id, intent, exclude_ids)
    if not candidates:
        return SelectionResult(), {}
    selection = await llm.select_recipes(user_query, compact(candidates))
    by_id = {r.id: r for r in candidates}
    # Страхування від галюцинацій: відкидаємо ID, яких немає серед кандидатів
    selection.selected_ids = [i for i in selection.selected_ids if i in by_id]
    selection.option_ids = [i for i in selection.option_ids if i in by_id]
    if selection.need_clarification and len(selection.option_ids) < 2:
        selection.need_clarification = False
    return selection, by_id
