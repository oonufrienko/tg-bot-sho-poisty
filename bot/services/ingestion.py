"""Перетворення повідомлення Telegram на вхід для екстракції рецепта."""

from dataclasses import dataclass, field

from aiogram import Bot
from aiogram.types import Message

MAX_FILE_BYTES = 19 * 1024 * 1024  # Bot API дозволяє завантажити до 20 МБ

PDF_MIME = "application/pdf"
IMAGE_MIMES = {"image/jpeg", "image/png", "image/webp", "image/heic"}


@dataclass
class RecipeInput:
    text: str | None = None
    files: list[tuple[bytes, str]] = field(default_factory=list)  # (bytes, mime)
    media: list[tuple[str, str]] = field(default_factory=list)  # (tg_file_id, type)
    source_type: str = "text"
    error: str | None = None


async def collect_input(message: Message, bot: Bot) -> RecipeInput:
    """Витягує текст і файли з повідомлення (фото/скрін/PDF/текст/форвард)."""
    result = RecipeInput()
    result.text = message.text or message.caption
    if message.forward_origin is not None:
        result.source_type = "forward"

    if message.photo:
        result.source_type = "photo" if result.source_type == "text" else result.source_type
        photo = message.photo[-1]  # найбільший розмір
        data = await _download(bot, photo.file_id)
        if data is None:
            result.error = "Не вдалося завантажити фото."
            return result
        result.files.append((data, "image/jpeg"))
        result.media.append((photo.file_id, "photo"))

    if message.document:
        doc = message.document
        mime = doc.mime_type or ""
        if mime == PDF_MIME or mime in IMAGE_MIMES:
            if (doc.file_size or 0) > MAX_FILE_BYTES:
                result.error = "Файл завеликий — Telegram дозволяє ботам до 20 МБ."
                return result
            data = await _download(bot, doc.file_id)
            if data is None:
                result.error = "Не вдалося завантажити файл."
                return result
            result.files.append((data, mime))
            result.media.append((doc.file_id, "pdf" if mime == PDF_MIME else "photo"))
            if result.source_type == "text":
                result.source_type = "pdf" if mime == PDF_MIME else "photo"
        else:
            result.error = "Такий тип файлу не підтримується. Надішліть фото, PDF або текст."
            return result

    return result


async def _download(bot: Bot, file_id: str) -> bytes | None:
    buffer = await bot.download(file_id)
    return buffer.read() if buffer else None
