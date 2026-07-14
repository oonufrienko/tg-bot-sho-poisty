"""Спільні ретраї для LLM-провайдерів з класифікацією за HTTP-статусом."""

import asyncio
import logging
from collections.abc import Awaitable, Callable

from bot.services.llm.base import LLMError, LLMQuotaError

logger = logging.getLogger(__name__)

RETRIES = 3
RETRY_DELAY = 5.0  # 5с, 10с — для 5xx і мережевих збоїв
QUOTA_RETRY_DELAY = 15.0  # 15с, 30с — для 429, щоб вікно ліміту встигло зсунутись
# Помилки конфігурації (ключ/модель/запит) — ретраїти немає сенсу
NO_RETRY_STATUSES = frozenset({400, 401, 403, 404})


def retry_delay(status: int | None, attempt: int) -> float | None:
    """Пауза перед наступною спробою; None = помилка постійна, не ретраїмо."""
    if status in NO_RETRY_STATUSES:
        return None
    if status == 429:
        return QUOTA_RETRY_DELAY * (attempt + 1)
    return RETRY_DELAY * (attempt + 1)


async def run_with_retries[T](
    attempt_call: Callable[[], Awaitable[T]],
    status_of: Callable[[Exception], int | None],
    provider: str,
) -> T:
    last_error: Exception | None = None
    last_status: int | None = None
    for attempt in range(RETRIES):
        try:
            return await attempt_call()
        except Exception as exc:  # noqa: BLE001 — класифікуємо збій нижче
            last_error, last_status = exc, status_of(exc)
            delay = retry_delay(last_status, attempt)
            if delay is None:
                logger.error(
                    "%s: постійна помилка (HTTP %s): %s", provider, last_status, exc
                )
                raise LLMError(
                    f"{provider}: помилка конфігурації (HTTP {last_status}): {exc}"
                ) from exc
            logger.warning(
                "LLM attempt %s failed (HTTP %s): %s", attempt + 1, last_status, exc
            )
            if attempt < RETRIES - 1:
                await asyncio.sleep(delay)
    if last_status == 429:
        raise LLMQuotaError(
            f"{provider}: перевищено ліміт запитів: {last_error}"
        ) from last_error
    raise LLMError(
        f"{provider} не відповів після {RETRIES} спроб: {last_error}"
    ) from last_error
