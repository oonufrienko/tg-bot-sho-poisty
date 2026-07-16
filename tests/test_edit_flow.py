"""Звʼязка «редагування → картка → Зберегти».

Ці інваріанти живуть у передачі edit_id між хендлерами, а не в repo, тож
тестами на repo вони не ловляться: одного разу забутий edit_id перетворив
редагування на створення копії.
"""

from datetime import datetime
from types import SimpleNamespace

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Chat, Message
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bot.db import repo
from bot.db.models import Base
from bot.handlers import add_recipe as ar
from bot.handlers import query as q
from bot.services.llm.base import RecipeExtraction


class _Msg(Message):
    """Хендлери роблять isinstance(..., Message), тож потрібен саме підклас."""

    async def answer(self, text, reply_markup=None, **kw):
        return self

    async def edit_reply_markup(self, reply_markup=None, **kw):
        return self


def _msg(text=None) -> _Msg:
    return _Msg(
        message_id=1, date=datetime.now(), chat=Chat(id=1, type="private"), text=text
    )


class _NoopTyping:
    """ChatActionSender вимагає справжнього Bot і зависає на його відсутності."""

    @classmethod
    def typing(cls, **kwargs):
        return cls()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class _LLM:
    def __init__(self, extraction):
        self.extraction = extraction
        self.prompts: list[str] = []

    async def extract_recipe(self, text, files):
        self.prompts.append(text)
        return self.extraction.model_copy(deep=True)


class _Query:
    def __init__(self):
        self.message = _msg()
        self.alerts: list[str] = []

    async def answer(self, text=None, show_alert=False):
        if text:
            self.alerts.append(text)


def _extraction(title="Борщ", ingredients=None):
    return RecipeExtraction(
        is_recipe=True,
        title=title,
        ingredients=ingredients if ingredients is not None else [],
        steps="Варити.",
        suggested_categories=["lunch"],
    )


@pytest.fixture
async def env():
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    state = FSMContext(
        storage=MemoryStorage(), key=StorageKey(bot_id=1, chat_id=1, user_id=1)
    )
    async with factory() as session:
        user = await repo.ensure_user(session, 1, "Тест")
        recipe = await repo.add_recipe(
            session,
            group_id=user.active_group_id,
            added_by=1,
            title="Борщ",
            ingredients=[{"name": "буряк", "qty": "2", "unit": "шт"}],
            steps="Варити.",
            categories=["lunch"],
            difficulty=1,
            calories=None,
            source_type="text",
            original_text="орig",
        )
        yield SimpleNamespace(session=session, user=user, recipe=recipe, state=state)
    await engine.dispose()


async def test_save_with_edit_id_updates_in_place(env):
    await ar.show_confirmation(
        _msg(),
        env.state,
        _extraction(ingredients=[{"name": "капуста", "qty": "1", "unit": "шт"}]),
        SimpleNamespace(source_type="text", media=[], text="орig"),
        edit_id=env.recipe.id,
    )
    await ar.save_recipe(_Query(), env.state, env.session, env.user)

    recipes = await repo.group_recipes(env.session, env.user.active_group_id)
    assert len(recipes) == 1, "оновлення не має створювати копію"
    assert [i["name"] for i in recipes[0].ingredients] == ["капуста"]


async def test_save_without_edit_id_adds_new(env):
    await ar.show_confirmation(
        _msg(),
        env.state,
        _extraction(title="Сирники"),
        SimpleNamespace(source_type="text", media=[], text="сирники"),
    )
    await ar.save_recipe(_Query(), env.state, env.session, env.user)

    titles = [r.title for r in await repo.group_recipes(env.session, env.user.active_group_id)]
    assert sorted(titles) == ["Борщ", "Сирники"]


async def test_apply_edit_carries_edit_id_into_the_card(env, monkeypatch):
    """Саме тут ховався баг: картка губила edit_id і «Зберегти» робило копію."""
    monkeypatch.setattr(q, "ChatActionSender", _NoopTyping)
    await env.state.set_state(q.ListStates.editing)
    await env.state.update_data(edit_id=env.recipe.id)
    llm = _LLM(_extraction(ingredients=[{"name": "капуста", "qty": "1", "unit": "шт"}]))

    await q.apply_edit(
        _msg("додай капусту"), env.state, env.session, env.user, llm, object()
    )

    data = await env.state.get_data()
    assert data["edit_id"] == env.recipe.id, "edit_id загублено дорогою до картки"
    assert "Поточний рецепт (JSON)" in llm.prompts[0]

    await ar.save_recipe(_Query(), env.state, env.session, env.user)
    recipes = await repo.group_recipes(env.session, env.user.active_group_id)
    assert len(recipes) == 1, "редагування створило копію замість оновлення"
    assert [i["name"] for i in recipes[0].ingredients] == ["капуста"]


async def test_edit_id_does_not_leak_into_next_add(env):
    """Покинуте редагування не має перетворити наступне додавання на перезапис."""
    await env.state.update_data(edit_id=env.recipe.id)  # ніби правку кинули

    await ar.show_confirmation(
        _msg(),
        env.state,
        _extraction(title="Новий пиріг"),
        SimpleNamespace(source_type="text", media=[], text="пиріг"),
    )
    assert (await env.state.get_data())["edit_id"] is None

    await ar.save_recipe(_Query(), env.state, env.session, env.user)
    titles = [r.title for r in await repo.group_recipes(env.session, env.user.active_group_id)]
    assert sorted(titles) == ["Борщ", "Новий пиріг"], "старий рецепт перезаписано!"
