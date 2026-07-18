from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import get_settings
from bot.db import repo
from bot.db.models import Group, User
from bot.keyboards.common import (
    BTN_GROUP,
    BTN_STATS,
    GroupCB,
    MoveRecipesCB,
    main_keyboard_for,
    move_recipes_keyboard,
)
from bot.services.openrouter_credits import fetch_remaining_credits

router = Router(name="group")


class GroupStates(StatesGroup):
    waiting_name = State()


async def _group_overview(message: Message, session: AsyncSession, user: User) -> None:
    groups = await repo.user_groups(session, user.tg_user_id)
    active = await repo.get_group(session, user.active_group_id) if user.active_group_id else None

    builder = InlineKeyboardBuilder()
    for group in groups:
        mark = "✅ " if active and group.id == active.id else ""
        builder.button(
            text=f"{mark}{group.name}",
            callback_data=GroupCB(action="switch", group_id=group.id),
        )
    builder.adjust(1)
    actions = InlineKeyboardBuilder()
    actions.button(text="➕ Створити групу", callback_data=GroupCB(action="create"))
    actions.button(text="🔗 Запрошення", callback_data=GroupCB(action="invite"))
    actions.button(text="👥 Учасники", callback_data=GroupCB(action="members"))
    actions.adjust(1)
    builder.attach(actions)

    active_name = escape(active.name) if active else "—"
    await message.answer(
        f"Активна група: <b>{active_name}</b>\n"
        "Рецепти додаються і шукаються саме в активній групі.\n"
        "Натисніть на групу, щоб переключитись:",
        reply_markup=builder.as_markup(),
    )


@router.message(F.text == BTN_GROUP)
async def group_menu(message: Message, session: AsyncSession, user: User) -> None:
    await _group_overview(message, session, user)


@router.message(F.text == BTN_STATS)
async def show_stats(message: Message, session: AsyncSession, user: User) -> None:
    settings = get_settings()
    # Кнопку бачать лише адміни, але текст може надіслати будь-хто —
    # перевіряємо на сервері.
    if user.tg_user_id not in settings.admin_ids:
        await message.answer("Лише для адмінів 🙂")
        return

    total_users = await repo.count_users(session)
    if settings.openrouter_api_key:
        remaining = await fetch_remaining_credits(settings.openrouter_api_key)
        credits_line = (
            f"💰 OpenRouter: ${remaining:.2f}"
            if remaining is not None
            else "💰 OpenRouter: не вдалося отримати"
        )
    else:
        credits_line = "💰 OpenRouter: не використовується"

    await message.answer(
        f"📊 <b>Статистика</b>\n\n👥 Користувачів: {total_users}\n{credits_line}"
    )


@router.callback_query(GroupCB.filter(F.action == "switch"))
async def switch_group(
    query: CallbackQuery, callback_data: GroupCB, session: AsyncSession, user: User
) -> None:
    groups = {g.id: g for g in await repo.user_groups(session, user.tg_user_id)}
    group = groups.get(callback_data.group_id)
    if group is None:
        await query.answer("Ви не учасник цієї групи", show_alert=True)
        return
    await repo.set_active_group(session, user, group.id)
    await query.answer(f"Активна група: {group.name}")
    if isinstance(query.message, Message):
        await _group_overview(query.message, session, user)


@router.callback_query(GroupCB.filter(F.action == "create"))
async def create_group_start(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(GroupStates.waiting_name)
    await query.answer()
    if isinstance(query.message, Message):
        await query.message.answer(
            "Як назвати групу? (наприклад: <b>Сім'я</b>)"
        )


async def offer_move_recipes(
    message: Message,
    session: AsyncSession,
    user: User,
    from_group_id: int | None,
    to_group: Group,
) -> None:
    """Пропонує перенести рецепти зі старої групи користувача в нову/спільну."""
    if from_group_id is None or from_group_id == to_group.id:
        return
    from_group = await repo.get_group(session, from_group_id)
    if from_group is None or from_group.owner_id != user.tg_user_id:
        return
    recipes = await repo.group_recipes(session, from_group_id)
    if not recipes:
        return
    await message.answer(
        f"У групі «{escape(from_group.name)}» у вас {len(recipes)} рецепт(ів).\n"
        f"Перенести їх у «{escape(to_group.name)}», щоб вони стали спільними?",
        reply_markup=move_recipes_keyboard(from_group_id, to_group.id),
    )


@router.message(GroupStates.waiting_name, F.text)
async def create_group_finish(
    message: Message, state: FSMContext, session: AsyncSession, user: User
) -> None:
    name = (message.text or "").strip()[:64]
    if not name:
        await message.answer("Надішліть назву групи текстом.")
        return
    prev_group_id = user.active_group_id
    group = await repo.create_group(session, name, user)
    await repo.set_active_group(session, user, group.id)
    await state.clear()
    bot_user = await message.bot.me()
    link = f"https://t.me/{bot_user.username}?start=g_{group.invite_token}"
    await message.answer(
        f"Групу <b>{escape(name)}</b> створено і зроблено активною 🎉\n\n"
        f"Запрошення для рідних (просто перешліть їм):\n{link}",
        reply_markup=main_keyboard_for(user),
    )
    await offer_move_recipes(message, session, user, prev_group_id, group)


@router.callback_query(MoveRecipesCB.filter(F.action == "move"))
async def move_recipes_confirm(
    query: CallbackQuery, callback_data: MoveRecipesCB, session: AsyncSession, user: User
) -> None:
    from_group = await repo.get_group(session, callback_data.from_group_id)
    member_ids = {g.id for g in await repo.user_groups(session, user.tg_user_id)}
    if (
        from_group is None
        or from_group.owner_id != user.tg_user_id
        or callback_data.to_group_id not in member_ids
    ):
        await query.answer("Немає доступу до цих груп", show_alert=True)
        return
    moved, skipped = await repo.move_recipes(
        session, callback_data.from_group_id, callback_data.to_group_id
    )
    await query.answer()
    if isinstance(query.message, Message):
        await query.message.edit_reply_markup(reply_markup=None)
        text = f"Перенесено {moved} рецепт(ів) ✅"
        if skipped:
            text += f"\nПропущено {skipped} — рецепти з такими назвами вже є в групі."
        await query.message.answer(text)


@router.callback_query(MoveRecipesCB.filter(F.action == "skip"))
async def move_recipes_skip(query: CallbackQuery) -> None:
    await query.answer()
    if isinstance(query.message, Message):
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.answer("Добре, залишаю як є 👌")


@router.callback_query(GroupCB.filter(F.action == "invite"))
async def invite_link(query: CallbackQuery, session: AsyncSession, user: User) -> None:
    group = await repo.get_group(session, user.active_group_id) if user.active_group_id else None
    await query.answer()
    if group is None or not isinstance(query.message, Message):
        return
    bot_user = await query.message.bot.me()
    link = f"https://t.me/{bot_user.username}?start=g_{group.invite_token}"
    await query.message.answer(
        f"Запрошення в групу <b>{escape(group.name)}</b> "
        f"(перешліть тому, кого хочете додати):\n{link}"
    )


@router.callback_query(GroupCB.filter(F.action == "members"))
async def members_list(query: CallbackQuery, session: AsyncSession, user: User) -> None:
    await query.answer()
    if user.active_group_id is None or not isinstance(query.message, Message):
        return
    group = await repo.get_group(session, user.active_group_id)
    members = await repo.group_members(session, user.active_group_id)
    names = "\n".join(f"• {escape(m.name)}" for m in members)
    await query.message.answer(
        f"Учасники групи <b>{escape(group.name) if group else ''}</b>:\n{names}"
    )
