from html import escape

from aiogram import Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import repo
from bot.db.models import User
from bot.keyboards.common import main_keyboard

router = Router(name="start")

WELCOME = (
    "Привіт! Я — сімейна база рецептів 👨‍🍳\n\n"
    "<b>Що я вмію:</b>\n"
    "• Надішліть мені рецепт — фото, скрін, PDF, текст або пересланий пост "
    "з каналу — я розпізнаю його і збережу у вашу базу.\n"
    "• Потім просто питайте: «що на вечерю?», «обіди з куркою», "
    "«меню на тиждень до 2000 ккал», «щось до чаю».\n"
    "• Я відповідаю ЛИШЕ рецептами з вашої бази — нічого не вигадую.\n\n"
    "Об'єднайте рідних у групу (кнопка «👨‍👩‍👧 Група») — і база буде спільною, "
    "а листування у кожного своє."
)

HELP = (
    "<b>Як користуватись:</b>\n\n"
    "➕ <b>Додати рецепт</b> — просто надішліть фото/скрін/PDF/текст рецепта. "
    "Я розпізнаю, запропоную категорії, ви підтвердите.\n\n"
    "🍽 <b>Спитати страву</b> — пишіть як зручно: «що сьогодні на десерт?», "
    "«що приготувати з курки?», «до чаю не солодке».\n\n"
    "📅 <b>Меню</b> — «меню на неділю», «меню на тиждень, 3 прийоми їжі, до 2000 ккал». "
    "Наприкінці дам список покупок, який можна переслати.\n"
    "Замінити позицію: «заміни вечерю дня 2».\n\n"
    "👨‍👩‍👧 <b>Група</b> — створіть групу, надішліть рідним запрошення — "
    "база рецептів стане спільною.\n\n"
    "Розумію українську, російську та англійську."
)


@router.message(CommandStart(deep_link=True))
async def start_with_link(
    message: Message, command: CommandObject, session: AsyncSession, user: User
) -> None:
    args = command.args or ""
    if args.startswith("g_"):
        group = await repo.join_group_by_token(session, args[2:], user)
        if group:
            await message.answer(
                f"Вітаю! Ви приєднались до групи <b>{escape(group.name)}</b> 🎉\n"
                "Тепер вам доступна спільна база рецептів цієї групи.",
                reply_markup=main_keyboard(),
            )
            return
        await message.answer(
            "Це запрошення недійсне 😔 Попросіть нове посилання.",
            reply_markup=main_keyboard(),
        )
        return
    await message.answer(WELCOME, reply_markup=main_keyboard())


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(WELCOME, reply_markup=main_keyboard())


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer(HELP, reply_markup=main_keyboard())
