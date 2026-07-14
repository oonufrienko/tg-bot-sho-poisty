"""Класифікація помилок LLM: 429 — довший ретрай, 4xx-конфіг — без ретраю."""

import pytest

from bot.services.llm import retry
from bot.services.llm.base import LLMError, LLMQuotaError
from bot.services.llm.retry import retry_delay, run_with_retries


class FakeAPIError(Exception):
    def __init__(self, status: int | None):
        super().__init__(f"HTTP {status}")
        self.status = status


def _status_of(exc: Exception) -> int | None:
    return getattr(exc, "status", None)


@pytest.mark.parametrize("status", [400, 401, 403, 404])
def test_config_errors_are_permanent(status):
    assert retry_delay(status, attempt=0) is None


def test_quota_uses_longer_delay():
    assert retry_delay(429, attempt=0) == retry.QUOTA_RETRY_DELAY
    assert retry_delay(429, attempt=1) == retry.QUOTA_RETRY_DELAY * 2
    assert retry_delay(429, attempt=0) > retry_delay(503, attempt=0)


@pytest.mark.parametrize("status", [500, 502, 503, None])
def test_transient_errors_use_standard_delay(status):
    assert retry_delay(status, attempt=0) == retry.RETRY_DELAY


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(retry, "RETRY_DELAY", 0.0)
    monkeypatch.setattr(retry, "QUOTA_RETRY_DELAY", 0.0)


async def test_permanent_error_fails_fast():
    calls = 0

    async def attempt():
        nonlocal calls
        calls += 1
        raise FakeAPIError(404)

    with pytest.raises(LLMError) as exc_info:
        await run_with_retries(attempt, _status_of, "Test")
    assert not isinstance(exc_info.value, LLMQuotaError)
    assert calls == 1


async def test_quota_exhaustion_raises_quota_error():
    calls = 0

    async def attempt():
        nonlocal calls
        calls += 1
        raise FakeAPIError(429)

    with pytest.raises(LLMQuotaError):
        await run_with_retries(attempt, _status_of, "Test")
    assert calls == retry.RETRIES


async def test_transient_error_recovers():
    calls = 0

    async def attempt():
        nonlocal calls
        calls += 1
        if calls < 3:
            raise FakeAPIError(503)
        return "ok"

    assert await run_with_retries(attempt, _status_of, "Test") == "ok"
    assert calls == 3
