from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.config import get_settings
from bot.db import repo
from bot.db.session import get_session_factory

DENIED_TEXT = (
    "Це приватний сімейний бот 🙈\n"
    "Попросіть власника додати ваш Telegram id у список дозволених."
)
NOT_CONFIGURED_TEXT = (
    "Доступ до бота ще не налаштовано 🔒\n"
    "Власнику: вкажіть Telegram id у ALLOWED_USER_IDS у файлі .env "
    "(або '*' для відкритого доступу) і перезапустіть бота."
)


class AccessDbMiddleware(BaseMiddleware):
    """Whitelist + сесія БД + реєстрація користувача для кожного апдейта."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user = data.get("event_from_user")
        if tg_user is None:
            return await handler(event, data)

        settings = get_settings()
        if not settings.allow_all and tg_user.id not in settings.allowed_ids:
            # Fail-closed: порожній whitelist нікого не пускає
            text = DENIED_TEXT if settings.allowed_ids else NOT_CONFIGURED_TEXT
            if isinstance(event, Message):
                await event.answer(text)
            elif isinstance(event, CallbackQuery):
                await event.answer(text, show_alert=True)
            return None

        async with get_session_factory()() as session:
            user = await repo.ensure_user(
                session, tg_user.id, tg_user.full_name or str(tg_user.id)
            )
            data["session"] = session
            data["user"] = user
            return await handler(event, data)
