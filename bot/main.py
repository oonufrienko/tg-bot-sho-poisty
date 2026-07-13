import asyncio
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig

from bot.config import get_settings
from bot.handlers import add_recipe, group, menu, query, start
from bot.middlewares import AccessDbMiddleware
from bot.services.llm.gemini import GeminiClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)


def run_migrations() -> None:
    Path(get_settings().database_path).parent.mkdir(parents=True, exist_ok=True)
    config = AlembicConfig(str(Path(__file__).resolve().parent.parent / "alembic.ini"))
    alembic_command.upgrade(config, "head")


async def main() -> None:
    settings = get_settings()
    await asyncio.to_thread(run_migrations)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    llm = GeminiClient(settings.gemini_api_key, settings.gemini_model)
    dp = Dispatcher(storage=MemoryStorage(), llm=llm)

    dp.message.outer_middleware(AccessDbMiddleware())
    dp.callback_query.outer_middleware(AccessDbMiddleware())

    # Порядок важливий: catch-all текстовий хендлер (query) — останній
    dp.include_routers(start.router, group.router, add_recipe.router, menu.router, query.router)

    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Почати / перезапустити"),
            BotCommand(command="help", description="Як користуватись"),
        ]
    )
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Бот запущено (long polling)")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
