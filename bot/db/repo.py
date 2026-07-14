from datetime import date, timedelta

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import (
    Group,
    GroupMember,
    Recipe,
    RecipeCategory,
    RecipeMedia,
    ServeHistory,
    User,
)


async def get_user(session: AsyncSession, tg_user_id: int) -> User | None:
    return await session.get(User, tg_user_id)


async def ensure_user(session: AsyncSession, tg_user_id: int, name: str) -> User:
    """Реєструє користувача при першому контакті й створює йому особисту групу."""
    user = await session.get(User, tg_user_id)
    if user is None:
        user = User(tg_user_id=tg_user_id, name=name)
        session.add(user)
        await session.flush()
        group = await create_group(session, "Мої рецепти", user)
        user.active_group_id = group.id
        await session.commit()
    return user


async def create_group(session: AsyncSession, name: str, owner: User) -> Group:
    group = Group(name=name, owner_id=owner.tg_user_id)
    session.add(group)
    await session.flush()
    session.add(GroupMember(group_id=group.id, user_id=owner.tg_user_id, role="owner"))
    await session.flush()
    return group


async def get_group(session: AsyncSession, group_id: int) -> Group | None:
    return await session.get(Group, group_id)


async def join_group_by_token(
    session: AsyncSession, token: str, user: User
) -> Group | None:
    group = (
        await session.execute(select(Group).where(Group.invite_token == token))
    ).scalar_one_or_none()
    if group is None:
        return None
    member = await session.get(GroupMember, (group.id, user.tg_user_id))
    if member is None:
        session.add(GroupMember(group_id=group.id, user_id=user.tg_user_id))
    user.active_group_id = group.id
    await session.commit()
    return group


async def user_groups(session: AsyncSession, user_id: int) -> list[Group]:
    rows = await session.execute(
        select(Group)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .where(GroupMember.user_id == user_id)
        .order_by(Group.id)
    )
    return list(rows.scalars())


async def group_members(session: AsyncSession, group_id: int) -> list[User]:
    rows = await session.execute(
        select(User)
        .join(GroupMember, GroupMember.user_id == User.tg_user_id)
        .where(GroupMember.group_id == group_id)
    )
    return list(rows.scalars())


async def set_active_group(session: AsyncSession, user: User, group_id: int) -> None:
    user.active_group_id = group_id
    await session.commit()


async def add_recipe(
    session: AsyncSession,
    *,
    group_id: int,
    added_by: int,
    title: str,
    ingredients: list[dict],
    steps: str,
    categories: list[str],
    difficulty: int | None,
    calories: int | None,
    source_type: str,
    original_text: str | None,
    media: list[tuple[str, str]] | None = None,  # (tg_file_id, media_type)
) -> Recipe:
    recipe = Recipe(
        group_id=group_id,
        added_by=added_by,
        title=title,
        ingredients=ingredients,
        steps=steps,
        difficulty=difficulty,
        calories=calories,
        source_type=source_type,
        original_text=original_text,
    )
    session.add(recipe)
    await session.flush()
    for cat in dict.fromkeys(categories):
        session.add(RecipeCategory(recipe_id=recipe.id, category=cat))
    for file_id, media_type in media or []:
        session.add(
            RecipeMedia(recipe_id=recipe.id, tg_file_id=file_id, media_type=media_type)
        )
    await session.commit()
    return await get_recipe(session, recipe.id, group_id)  # type: ignore[return-value]


def _norm_title(title: str) -> str:
    """Нормалізація для порівняння назв: SQL lower() не вміє кирилицю."""
    return " ".join(title.split()).casefold()


async def find_recipe_by_title(
    session: AsyncSession, group_id: int, title: str
) -> Recipe | None:
    wanted = _norm_title(title)
    rows = await session.execute(select(Recipe).where(Recipe.group_id == group_id))
    for recipe in rows.scalars():
        if _norm_title(recipe.title) == wanted:
            return recipe
    return None


async def move_recipes(
    session: AsyncSession, from_group_id: int, to_group_id: int
) -> tuple[int, int]:
    """Переносить рецепти між групами разом з історією подач.

    Рецепт, чия назва (нормалізовано) вже є в цільовій групі, пропускається —
    однакова назва не гарантує однаковий вміст, тому нічого не видаляємо.
    Повертає (перенесено, пропущено_дублікатів).
    """
    target_titles = {
        _norm_title(title)
        for title in (
            await session.execute(
                select(Recipe.title).where(Recipe.group_id == to_group_id)
            )
        ).scalars()
    }
    rows = await session.execute(select(Recipe).where(Recipe.group_id == from_group_id))
    moved_ids: list[int] = []
    skipped = 0
    for recipe in rows.scalars():
        norm = _norm_title(recipe.title)
        if norm in target_titles:
            skipped += 1
            continue
        recipe.group_id = to_group_id
        target_titles.add(norm)
        moved_ids.append(recipe.id)
    if moved_ids:
        await session.execute(
            update(ServeHistory)
            .where(
                ServeHistory.group_id == from_group_id,
                ServeHistory.recipe_id.in_(moved_ids),
            )
            .values(group_id=to_group_id)
        )
    await session.commit()
    return len(moved_ids), skipped


async def get_recipe(
    session: AsyncSession, recipe_id: int, group_id: int
) -> Recipe | None:
    """recipe_id приходить із callback-data (клієнтські дані) — завжди
    перевіряємо належність рецепта групі, інакше можливий доступ до чужої бази."""
    return (
        await session.execute(
            select(Recipe).where(Recipe.id == recipe_id, Recipe.group_id == group_id)
        )
    ).scalar_one_or_none()


async def group_recipes(
    session: AsyncSession, group_id: int, categories: list[str] | None = None
) -> list[Recipe]:
    query = select(Recipe).where(Recipe.group_id == group_id)
    if categories:
        query = query.join(
            RecipeCategory, RecipeCategory.recipe_id == Recipe.id
        ).where(RecipeCategory.category.in_(categories)).distinct()
    rows = await session.execute(query.order_by(Recipe.created_at.desc()))
    return list(rows.scalars().unique())


async def recent_recipes(
    session: AsyncSession, group_id: int, limit: int = 10
) -> list[Recipe]:
    rows = await session.execute(
        select(Recipe)
        .where(Recipe.group_id == group_id)
        .order_by(Recipe.created_at.desc())
        .limit(limit)
    )
    return list(rows.scalars().unique())


async def set_recipe_categories(
    session: AsyncSession, recipe_id: int, categories: list[str]
) -> None:
    await session.execute(
        delete(RecipeCategory).where(RecipeCategory.recipe_id == recipe_id)
    )
    for cat in dict.fromkeys(categories):
        session.add(RecipeCategory(recipe_id=recipe_id, category=cat))
    await session.commit()


async def record_serve(
    session: AsyncSession,
    *,
    group_id: int,
    recipe_id: int,
    user_id: int,
    meal_type: str | None,
    served_on: date | None = None,
) -> None:
    session.add(
        ServeHistory(
            group_id=group_id,
            recipe_id=recipe_id,
            user_id=user_id,
            meal_type=meal_type,
            served_on=served_on or date.today(),
        )
    )
    await session.commit()


async def recently_served_ids(
    session: AsyncSession, group_id: int, days: int = 7
) -> set[int]:
    """Рецепти, які подавались за останні `days` днів — для правила неповторення."""
    since = date.today() - timedelta(days=days)
    rows = await session.execute(
        select(ServeHistory.recipe_id).where(
            ServeHistory.group_id == group_id, ServeHistory.served_on >= since
        )
    )
    return set(rows.scalars())


async def recent_served(
    session: AsyncSession, group_id: int, limit: int = 10
) -> list[tuple[ServeHistory, Recipe]]:
    rows = await session.execute(
        select(ServeHistory, Recipe)
        .join(Recipe, Recipe.id == ServeHistory.recipe_id)
        .where(ServeHistory.group_id == group_id)
        .order_by(ServeHistory.id.desc())
        .limit(limit)
    )
    return [(sh, r) for sh, r in rows.all()]
