from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import repo
from bot.db.models import User
from bot.keyboards.common import BTN_GROUP, GroupCB, main_keyboard

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


@router.message(GroupStates.waiting_name, F.text)
async def create_group_finish(
    message: Message, state: FSMContext, session: AsyncSession, user: User
) -> None:
    name = (message.text or "").strip()[:64]
    if not name:
        await message.answer("Надішліть назву групи текстом.")
        return
    group = await repo.create_group(session, name, user)
    await repo.set_active_group(session, user, group.id)
    await state.clear()
    bot_user = await message.bot.me()
    link = f"https://t.me/{bot_user.username}?start=g_{group.invite_token}"
    await message.answer(
        f"Групу <b>{escape(name)}</b> створено і зроблено активною 🎉\n\n"
        f"Запрошення для рідних (просто перешліть їм):\n{link}",
        reply_markup=main_keyboard(),
    )


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
