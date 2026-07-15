from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bot.config import get_settings

_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _engine, _session_factory
    if _session_factory is None:
        _engine = create_async_engine(get_settings().db_url)

        @event.listens_for(_engine.sync_engine, "connect")
        def _set_pragmas(dbapi_connection, _record):
            cursor = dbapi_connection.cursor()
            # Сесія живе весь час хендлера, зокрема на час LLM-виклику (5-30с).
            # Без WAL відкрита read-транзакція блокує паралельний запис, і кнопка
            # «Зберегти» висить, доки не завершиться чужий запит до AI.
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    return _session_factory
