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


async def test_count_users(session):
    assert await repo.count_users(session) == 0
    await repo.ensure_user(session, 1, "Перший")
    await repo.ensure_user(session, 2, "Друга")
    await repo.ensure_user(session, 1, "Перший знову")  # не дублюється
    assert await repo.count_users(session) == 2


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


async def test_delete_recipe_removes_serve_history(session):
    """ServeHistory має FK на recipes.id без cascade — історію треба прибрати явно."""
    user, recipe = await _make_user_with_recipe(session)
    await repo.record_serve(
        session,
        group_id=user.active_group_id,
        recipe_id=recipe.id,
        user_id=user.tg_user_id,
        meal_type="lunch",
        served_on=date.today(),
    )
    assert await repo.delete_recipe(session, recipe.id, user.active_group_id) == "Борщ"
    assert await repo.group_recipes(session, user.active_group_id) == []
    assert await repo.recently_served_ids(session, user.active_group_id, days=7) == set()


async def test_update_recipe_replaces_fields_and_categories(session):
    user, recipe = await _make_user_with_recipe(session)  # "Борщ", lunch
    updated = await repo.update_recipe(
        session,
        recipe.id,
        user.active_group_id,
        title="Зелений борщ",
        ingredients=[{"name": "щавель", "qty": "1", "unit": "пучок"}],
        steps="Варити зі щавлем.",
        categories=["dinner", "salad"],
        difficulty=3,
        calories=450,
    )
    assert updated is not None
    assert updated.id == recipe.id  # той самий запис, не копія
    assert updated.title == "Зелений борщ"
    assert [i["name"] for i in updated.ingredients] == ["щавель"]
    assert sorted(updated.category_keys) == ["dinner", "salad"]
    assert (updated.difficulty, updated.calories) == (3, 450)
    assert len(await repo.group_recipes(session, user.active_group_id)) == 1


async def test_update_recipe_keeps_origin_and_serve_history(session):
    """Правка міняє текст рецепта, а не його походження чи історію подач."""
    user, recipe = await _make_user_with_recipe(session)
    await repo.record_serve(
        session,
        group_id=user.active_group_id,
        recipe_id=recipe.id,
        user_id=user.tg_user_id,
        meal_type="lunch",
        served_on=date.today(),
    )
    updated = await repo.update_recipe(
        session,
        recipe.id,
        user.active_group_id,
        title="Борщ",
        ingredients=[],
        steps="Інакше.",
        categories=["lunch"],
        difficulty=None,
        calories=None,
    )
    assert updated is not None
    assert updated.source_type == "text"
    assert recipe.id in await repo.recently_served_ids(
        session, user.active_group_id, days=7
    )


async def test_update_recipe_enforces_group_isolation(session):
    user, recipe = await _make_user_with_recipe(session)
    stranger = await repo.ensure_user(session, 2, "Сусідка")
    assert (
        await repo.update_recipe(
            session,
            recipe.id,
            stranger.active_group_id,
            title="Викрадений борщ",
            ingredients=[],
            steps="",
            categories=["lunch"],
            difficulty=None,
            calories=None,
        )
        is None
    )
    untouched = await repo.get_recipe(session, recipe.id, user.active_group_id)
    assert untouched is not None and untouched.title == "Борщ"


async def test_delete_recipe_enforces_group_isolation(session):
    user, recipe = await _make_user_with_recipe(session, tg_id=1)
    stranger = await repo.ensure_user(session, 2, "Сусідка")
    assert await repo.delete_recipe(session, recipe.id, stranger.active_group_id) is None
    assert [r.id for r in await repo.group_recipes(session, user.active_group_id)] == [
        recipe.id
    ]


async def test_join_group_by_token_shares_base(session):
    user1, recipe = await _make_user_with_recipe(session, tg_id=1)
    group = await repo.get_group(session, user1.active_group_id)
    user2 = await repo.ensure_user(session, 2, "Дружина")
    joined = await repo.join_group_by_token(session, group.invite_token, user2)
    assert joined is not None and joined.id == group.id
    shared = await repo.group_recipes(session, user2.active_group_id)
    assert [r.id for r in shared] == [recipe.id]


async def test_create_group_then_invite_shares_recipes(session):
    """Сценарій бага: створив нову групу → переніс рецепти → запрошений їх бачить."""
    user1, recipe = await _make_user_with_recipe(session, tg_id=1)
    personal_group_id = user1.active_group_id
    family = await repo.create_group(session, "Сім'я", user1)
    await repo.set_active_group(session, user1, family.id)

    moved, skipped = await repo.move_recipes(session, personal_group_id, family.id)
    assert (moved, skipped) == (1, 0)

    user2 = await repo.ensure_user(session, 2, "Дружина")
    joined = await repo.join_group_by_token(session, family.invite_token, user2)
    assert joined is not None
    shared = await repo.group_recipes(session, user2.active_group_id)
    assert [r.id for r in shared] == [recipe.id]
    assert await repo.group_recipes(session, personal_group_id) == []


async def test_move_recipes_transfers_serve_history(session):
    user, recipe = await _make_user_with_recipe(session)
    old_group_id = user.active_group_id
    await repo.record_serve(
        session,
        group_id=old_group_id,
        recipe_id=recipe.id,
        user_id=user.tg_user_id,
        meal_type="lunch",
        served_on=date.today(),
    )
    family = await repo.create_group(session, "Сім'я", user)
    await repo.move_recipes(session, old_group_id, family.id)
    assert recipe.id in await repo.recently_served_ids(session, family.id, days=7)
    assert await repo.recently_served_ids(session, old_group_id, days=7) == set()


async def test_move_recipes_skips_duplicates_by_title(session):
    """Дублікат за назвою (інший регістр/пробіли) лишається у старій групі."""
    user, recipe = await _make_user_with_recipe(session)  # "Борщ"
    old_group_id = user.active_group_id
    family = await repo.create_group(session, "Сім'я", user)
    await repo.add_recipe(
        session,
        group_id=family.id,
        added_by=user.tg_user_id,
        title="  борщ ",
        ingredients=[],
        steps="Інший варіант.",
        categories=["lunch"],
        difficulty=None,
        calories=None,
        source_type="text",
        original_text=None,
    )
    moved, skipped = await repo.move_recipes(session, old_group_id, family.id)
    assert (moved, skipped) == (0, 1)
    left_behind = await repo.group_recipes(session, old_group_id)
    assert [r.id for r in left_behind] == [recipe.id]


async def test_find_recipe_by_title_normalizes_and_isolates(session):
    user, recipe = await _make_user_with_recipe(session)  # "Борщ"
    found = await repo.find_recipe_by_title(session, user.active_group_id, " борщ  ")
    assert found is not None and found.id == recipe.id
    stranger = await repo.ensure_user(session, 2, "Сусідка")
    assert (
        await repo.find_recipe_by_title(session, stranger.active_group_id, "Борщ")
        is None
    )


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


async def test_clear_served_wipes_history_for_group_only(session):
    user, recipe = await _make_user_with_recipe(session, tg_id=1)
    stranger, their_recipe = await _make_user_with_recipe(session, tg_id=2)
    for u, r in ((user, recipe), (stranger, their_recipe)):
        await repo.record_serve(
            session,
            group_id=u.active_group_id,
            recipe_id=r.id,
            user_id=u.tg_user_id,
            meal_type="lunch",
            served_on=date.today(),
        )

    await repo.clear_served(session, user.active_group_id)

    assert await repo.recent_served(session, user.active_group_id) == []
    # після очищення страви одразу можуть рекомендуватись знову
    assert await repo.recently_served_ids(session, user.active_group_id, days=7) == set()
    # чужа група лишається як була
    assert len(await repo.recent_served(session, stranger.active_group_id)) == 1
