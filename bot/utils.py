from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, Message

TG_LIMIT = 4096


async def send_long(
    message: Message,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Надсилає довгий текст кількома повідомленнями, ріжучи по рядках.

    Клавіатура чіпляється до останнього шматка.
    """
    chunks: list[str] = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > TG_LIMIT:
            chunks.append(current)
            current = line
        else:
            current = f"{current}\n{line}" if current else line
    if current:
        chunks.append(current)

    for i, chunk in enumerate(chunks):
        is_last = i == len(chunks) - 1
        await message.answer(
            chunk,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup if is_last else None,
        )
