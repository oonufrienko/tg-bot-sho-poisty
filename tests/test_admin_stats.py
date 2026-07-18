"""Адмін-статистика: парсинг admin_ids, лічильник, баланс, гвард хендлера."""

from datetime import datetime

import httpx
import pytest
from aiogram.types import Chat, Message
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bot.config import Settings, get_settings
from bot.db import repo
from bot.db.models import Base
from bot.handlers.group import show_stats
from bot.services.openrouter_credits import fetch_remaining_credits


def make_settings(**kw) -> Settings:
    return Settings(_env_file=None, bot_token="x", openrouter_api_key="y", **kw)


# --- config.admin_ids ------------------------------------------------------


def test_admin_ids_empty_means_no_admins():
    assert make_settings().admin_ids == frozenset()


def test_admin_ids_parses_commas_and_spaces():
    s = make_settings(admin_user_ids=" 123, 456 ,789")
    assert s.admin_ids == frozenset({123, 456, 789})


def test_admin_ids_has_no_star_magic():
    """'*' — не «всі адміни», а помилка конфігурації: явний ValueError."""
    with pytest.raises(ValueError):
        make_settings(admin_user_ids="*").admin_ids


# --- services.openrouter_credits -------------------------------------------


def credits_client(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def test_fetch_remaining_credits_returns_difference():
    def handler(request):
        assert request.headers["Authorization"] == "Bearer sk-test"
        return httpx.Response(
            200, json={"data": {"total_credits": 10.0, "total_usage": 5.17}}
        )

    async with credits_client(handler) as client:
        assert await fetch_remaining_credits("sk-test", client) == pytest.approx(4.83)


async def test_fetch_remaining_credits_none_on_http_error():
    async with credits_client(lambda r: httpx.Response(401, json={})) as client:
        assert await fetch_remaining_credits("bad", client) is None


async def test_fetch_remaining_credits_none_on_malformed_json():
    async with credits_client(
        lambda r: httpx.Response(200, json={"data": {"whatever": 1}})
    ) as client:
        assert await fetch_remaining_credits("sk", client) is None


# --- хендлер: гвард адмінства ----------------------------------------------


class _Msg(Message):
    async def answer(self, text, **kw):
        sent.append(text)
        return self


sent: list[str] = []


class _Query:
    def __init__(self):
        self.message = _Msg(
            message_id=1, date=datetime.now(), chat=Chat(id=1, type="private")
        )
        self.alerts: list[str] = []

    async def answer(self, text=None, show_alert=False):
        if text:
            self.alerts.append(text)


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_sessionmaker(engine, expire_on_commit=False)() as s:
        yield s
    await engine.dispose()


async def test_non_admin_gets_alert_even_with_forged_callback(session, monkeypatch):
    """Кнопки не-адмін не бачить, але callback_data підробна — гвард на сервері."""
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("OPENROUTER_API_KEY", "y")
    monkeypatch.setenv("ADMIN_USER_IDS", "999")
    get_settings.cache_clear()
    try:
        user = await repo.ensure_user(session, 1, "Не адмін")
        sent.clear()
        query = _Query()
        await show_stats(query, session, user)
        assert query.alerts == ["Лише для адмінів"]
        assert sent == []
    finally:
        get_settings.cache_clear()


async def test_admin_sees_user_count_and_credits(session, monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
    monkeypatch.setenv("ADMIN_USER_IDS", "1")
    get_settings.cache_clear()

    async def fake_credits(api_key, client=None):
        assert api_key == "sk-test"
        return 4.83

    import bot.handlers.group as group_module

    monkeypatch.setattr(group_module, "fetch_remaining_credits", fake_credits)
    try:
        admin = await repo.ensure_user(session, 1, "Адмін")
        await repo.ensure_user(session, 2, "Ще хтось")
        sent.clear()
        await show_stats(_Query(), session, admin)
        assert len(sent) == 1
        assert "Користувачів: 2" in sent[0]
        assert "$4.83" in sent[0]
    finally:
        get_settings.cache_clear()
