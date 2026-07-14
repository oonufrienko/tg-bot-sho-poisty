from datetime import date, timedelta

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bot.db import repo
from bot.db.models import Base


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


async def _make_user_with_recipe(session, tg_id=1, categories=None):
    user = await repo.ensure_user(session, tg_id, "Тест")
    recipe = await repo.add_recipe(
        session,
        group_id=user.active_group_id,
        added_by=user.tg_user_id,
        title="Борщ",
        ingredients=[{"name": "буряк", "qty": "2", "unit": "шт"}],
        steps="Варити.",
        categories=categories or ["lunch"],
        difficulty=2,
        calories=None,
        source_type="text",
        original_text=None,
    )
    return user, recipe


async def test_ensure_user_creates_personal_group(session):
    user = await repo.ensure_user(session, 42, "Олексій")
    assert user.active_group_id is not None
    groups = await repo.user_groups(session, 42)
    assert len(groups) == 1
    assert groups[0].name == "Мої рецепти"


async def test_groups_are_isolated(session):
    user1, _ = await _make_user_with_recipe(session, tg_id=1)
    user2 = await repo.ensure_user(session, 2, "Сусідка")
    theirs = await repo.group_recipes(session, user2.active_group_id)
    assert theirs == []
    ours = await repo.group_recipes(session, user1.active_group_id)
    assert len(ours) == 1


async def test_get_recipe_enforces_group_isolation(session):
    """recipe_id з callback-data не має відкривати рецепти чужої групи."""
    user, recipe = await _make_user_with_recipe(session, tg_id=1)
    stranger = await repo.ensure_user(session, 2, "Сусідка")
    assert await repo.get_recipe(session, recipe.id, user.active_group_id) is not None
    assert await repo.get_recipe(session, recipe.id, stranger.active_group_id) is None


async def test_join_group_by_token_shares_base(session):
    user1, recipe = await _make_user_with_recipe(session, tg_id=1)
    group = await repo.get_group(session, user1.active_group_id)
    user2 = await repo.ensure_user(session, 2, "Дружина")
    joined = await repo.join_group_by_token(session, group.invite_token, user2)
    assert joined is not None and joined.id == group.id
    shared = await repo.group_recipes(session, user2.active_group_id)
    assert [r.id for r in shared] == [recipe.id]


async def test_no_repeat_rule_window(session):
    user, recipe = await _make_user_with_recipe(session)
    await repo.record_serve(
        session,
        group_id=user.active_group_id,
        recipe_id=recipe.id,
        user_id=user.tg_user_id,
        meal_type="lunch",
        served_on=date.today() - timedelta(days=3),
    )
    recent = await repo.recently_served_ids(session, user.active_group_id, days=7)
    assert recipe.id in recent
    older = await repo.recently_served_ids(session, user.active_group_id, days=2)
    assert recipe.id not in older


async def test_category_filter(session):
    user, _ = await _make_user_with_recipe(session, categories=["lunch"])
    await repo.add_recipe(
        session,
        group_id=user.active_group_id,
        added_by=user.tg_user_id,
        title="Сирники",
        ingredients=[{"name": "сир", "qty": "400", "unit": "г"}],
        steps="Смажити.",
        categories=["breakfast", "dessert"],
        difficulty=1,
        calories=None,
        source_type="text",
        original_text=None,
    )
    breakfast = await repo.group_recipes(session, user.active_group_id, ["breakfast"])
    assert [r.title for r in breakfast] == ["Сирники"]
    both = await repo.group_recipes(session, user.active_group_id, ["lunch", "breakfast"])
    assert len(both) == 2
