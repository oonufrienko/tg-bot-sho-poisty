"""Голе число зі «Весь список» → показ рецепта.

Головний ризик фічі — зачепити звичайний текст, тож окремо перевіряємо, що
фільтр спрацьовує лише на повідомленні, яке ЦІЛКОМ є числом.
"""

import re
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
from bot.handlers import query as q


class _Msg(Message):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, "sent", [])

    async def answer(self, text, reply_markup=None, **kw):
        self.sent.append(text)
        return self

    async def answer_photo(self, file_id, **kw):
        self.sent.append(f"photo:{file_id}")
        return self


def _msg(text=None) -> _Msg:
    return _Msg(
        message_id=1, date=datetime.now(), chat=Chat(id=1, type="private"), text=text
    )


async def _add(session, group_id, title):
    return await repo.add_recipe(
        session,
        group_id=group_id,
        added_by=1,
        title=title,
        ingredients=[{"name": "буряк", "qty": "2", "unit": "шт"}],
        steps="Варити.",
        categories=["lunch"],
        difficulty=None,
        calories=None,
        source_type="text",
        original_text=None,
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
        borsch = await _add(session, user.active_group_id, "Борщ")
        plov = await _add(session, user.active_group_id, "Плов")
        await state.update_data(list_ids=[borsch.id, plov.id])
        yield SimpleNamespace(
            session=session, user=user, state=state, borsch=borsch, plov=plov
        )
    await engine.dispose()


async def test_number_opens_the_matching_recipe(env):
    message = _msg("2")
    await q.open_by_number(message, env.state, env.session, env.user)
    assert "Плов" in message.sent[0]
    assert "Борщ" not in message.sent[0]


async def test_number_with_dot_works(env):
    """Номер копіюють зі списку разом із крапкою."""
    message = _msg("1.")
    await q.open_by_number(message, env.state, env.session, env.user)
    assert "Борщ" in message.sent[0]


async def test_number_out_of_range_hints_the_range(env):
    message = _msg("99")
    await q.open_by_number(message, env.state, env.session, env.user)
    assert message.sent == ["Потрібен номер від 1 до 2."]


async def test_without_open_list_asks_to_open_it(env):
    await env.state.update_data(list_ids=[])
    message = _msg("1")
    await q.open_by_number(message, env.state, env.session, env.user)
    assert message.sent == [q.LIST_GONE]


async def test_recipe_from_another_group_is_not_shown(env):
    """list_ids міг лишитись від попередньої групи — рецепт не має витекти."""
    other = await repo.create_group(env.session, "Інша", env.user)
    stranger = await _add(env.session, other.id, "Чужий пиріг")
    await env.state.update_data(list_ids=[stranger.id])

    message = _msg("1")
    await q.open_by_number(message, env.state, env.session, env.user)
    assert message.sent == [q.LIST_GONE]


@pytest.mark.parametrize(
    "text, matches",
    [
        ("78", True),
        ("78.", True),
        ("  3  ", True),
        ("500 г борошна, 2 яйця", False),  # текст рецепта
        ("меню на 3 дні", False),
        ("2 персони", False),
        ("78 борщ", False),
        ("", False),
    ],
)
def test_filter_matches_only_bare_numbers(text, matches):
    assert bool(re.match(q.NUMBER_ONLY, text)) is matches
