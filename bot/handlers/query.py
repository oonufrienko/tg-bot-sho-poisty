from datetime import date
from html import escape

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import repo
from bot.db.models import MEAL_LABELS, User
from bot.handlers.add_recipe import start_recipe_flow
from bot.handlers.menu import run_menu_flow, run_replace_flow
from bot.handlers.start import HELP
from bot.keyboards.common import (
    BTN_ASK,
    BTN_RECENT,
    DishCB,
    RecentCB,
    dish_keyboard,
    options_keyboard,
    recent_keyboard,
)
from bot.rendering import render_recipe
from bot.services import retrieval
from bot.services.ingestion import collect_input
from bot.services.llm.base import LLMClient, LLMError, QueryIntent
from bot.utils import send_long

router = Router(name="query")


@router.message(F.text == BTN_ASK)
async def ask_hint(message: Message) -> None:
    await message.answer(
        "Просто спитайте, наприклад:\n"
        "• «що сьогодні на вечерю?»\n"
        "• «що приготувати з курки?»\n"
        "• «щось до чаю, не солодке»\n"
        "• «покажи обіди з яловичиною»"
    )


@router.message(F.text == BTN_RECENT)
async def recent_hint(message: Message) -> None:
    await message.answer("Які страви показати?", reply_markup=recent_keyboard())


@router.callback_query(RecentCB.filter())
async def recent_list(
    query: CallbackQuery, callback_data: RecentCB, session: AsyncSession, user: User
) -> None:
    await query.answer()
    if user.active_group_id is None or not isinstance(query.message, Message):
        return
    if callback_data.kind == "added":
        recipes = await repo.recent_recipes(session, user.active_group_id, limit=10)
        if not recipes:
            await query.message.answer("У базі поки немає рецептів.")
            return
        lines = ["🕐 <b>Останні додані страви:</b>\n"]
        lines += [f"{i}. {escape(r.title)}" for i, r in enumerate(recipes, 1)]
    else:
        served = await repo.recent_served(session, user.active_group_id, limit=10)
        if not served:
            await query.message.answer("Я ще нічого не рекомендував 🙂")
            return
        lines = ["🕐 <b>Останні рекомендовані страви:</b>\n"]
        lines += [
            f"{i}. {escape(r.title)}"
            + (f" ({MEAL_LABELS[sh.meal_type]}, {sh.served_on:%d.%m})"
               if sh.meal_type in MEAL_LABELS else f" ({sh.served_on:%d.%m})")
            for i, (sh, r) in enumerate(served, 1)
        ]
    await send_long(query.message, "\n".join(lines))


def _meal_type(intent: QueryIntent) -> str | None:
    for meal in intent.meal_types:
        if meal in MEAL_LABELS:
            return meal
    return None


async def show_dish(
    message: Message, state: FSMContext, recipe, shown_ids: list[int]
) -> None:
    await state.update_data(q_shown=shown_ids)
    await send_long(message, render_recipe(recipe), reply_markup=dish_keyboard(recipe.id))
    if recipe.media:
        photo = next((m for m in recipe.media if m.media_type == "photo"), None)
        if photo:
            await message.answer_photo(photo.tg_file_id)


async def run_find_dish(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user: User,
    llm: LLMClient,
    text: str,
    intent: QueryIntent,
    exclude_ids: set[int] = frozenset(),
) -> None:
    if user.active_group_id is None:
        return
    selection, by_id = await retrieval.find_dish(
        session, llm, user.active_group_id, text, intent, exclude_ids
    )
    await state.update_data(q_text=text, q_intent=intent.model_dump())

    if selection.need_clarification and selection.option_ids:
        options = [(i, by_id[i].title) for i in selection.option_ids]
        await state.update_data(q_shown=list(exclude_ids))
        await message.answer(
            selection.clarification_question or "Оберіть варіант:",
            reply_markup=options_keyboard(options),
        )
        return

    if not selection.selected_ids:
        if exclude_ids:
            await message.answer(
                "Більше нічого підходящого в базі немає 😔 Додайте нових рецептів!"
            )
        else:
            await message.answer(
                "Не знайшов нічого підходящого у вашій базі 😔\n"
                "Додайте рецепт — надішліть фото, текст чи PDF."
            )
        return

    recipe = by_id[selection.selected_ids[0]]
    await show_dish(message, state, recipe, list(exclude_ids) + [recipe.id])


@router.callback_query(DishCB.filter(F.action == "take"))
async def take_dish(
    query: CallbackQuery,
    callback_data: DishCB,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    if user.active_group_id is None:
        await query.answer()
        return
    data = await state.get_data()
    intent = QueryIntent.model_validate(data["q_intent"]) if data.get("q_intent") else None
    await repo.record_serve(
        session,
        group_id=user.active_group_id,
        recipe_id=callback_data.recipe_id,
        user_id=user.tg_user_id,
        meal_type=_meal_type(intent) if intent else None,
        served_on=date.today(),
    )
    await query.answer("Смачного! Цю страву не повторюватиму тиждень 👍")


@router.callback_query(DishCB.filter(F.action == "another"))
async def another_dish(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
    llm: LLMClient,
) -> None:
    await query.answer()
    if not isinstance(query.message, Message):
        return
    data = await state.get_data()
    if not data.get("q_text"):
        await query.message.answer("Спитайте мене заново, що підібрати 🙂")
        return
    intent = QueryIntent.model_validate(data["q_intent"])
    await run_find_dish(
        query.message,
        state,
        session,
        user,
        llm,
        data["q_text"],
        intent,
        exclude_ids=set(data.get("q_shown", [])),
    )


@router.callback_query(DishCB.filter(F.action == "choose"))
async def choose_dish(
    query: CallbackQuery,
    callback_data: DishCB,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    await query.answer()
    if not isinstance(query.message, Message):
        return
    recipe = await repo.get_recipe(session, callback_data.recipe_id)
    if recipe is None:
        return
    data = await state.get_data()
    shown = data.get("q_shown", []) + [recipe.id]
    await show_dish(query.message, state, recipe, shown)


@router.message(F.text, ~F.text.startswith("/"))
async def free_text(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user: User,
    bot: Bot,
    llm: LLMClient,
) -> None:
    text = message.text or ""
    try:
        intent = await llm.route_query(text)
    except LLMError:
        await message.answer("Сервіс AI зараз недоступний, спробуйте за хвилину 🙏")
        return

    match intent.intent:
        case "add_recipe":
            recipe_input = await collect_input(message, bot)
            await start_recipe_flow(message, state, llm, recipe_input)
        case "find_dish":
            await run_find_dish(message, state, session, user, llm, text, intent)
        case "another_suggestion":
            data = await state.get_data()
            if data.get("q_text"):
                previous = QueryIntent.model_validate(data["q_intent"])
                await run_find_dish(
                    message, state, session, user, llm,
                    data["q_text"], previous,
                    exclude_ids=set(data.get("q_shown", [])),
                )
            else:
                await run_find_dish(message, state, session, user, llm, text, intent)
        case "plan_menu":
            await run_menu_flow(message, state, session, user, llm, text, intent)
        case "replace_slot":
            await run_replace_flow(message, state, session, user, llm, text, intent)
        case "recent_dishes":
            await message.answer("Які страви показати?", reply_markup=recent_keyboard())
        case _:
            await message.answer(HELP)
