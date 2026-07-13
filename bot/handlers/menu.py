from datetime import date

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import repo
from bot.db.models import MEAL_LABELS, User
from bot.keyboards.common import BTN_MENU, MenuCB, menu_keyboard
from bot.rendering import render_menu_day, render_shopping_list
from bot.services import menu_planner, shopping_list
from bot.services.llm.base import LLMClient, QueryIntent
from bot.utils import send_long

router = Router(name="menu")


@router.message(F.text == BTN_MENU)
async def menu_hint(message: Message) -> None:
    await message.answer(
        "Напишіть, яке меню скласти, наприклад:\n"
        "• «меню на неділю»\n"
        "• «меню на тиждень, до 2000 ккал»\n"
        "• «меню на 3 дні, 2 прийоми їжі, на 4 персони»\n\n"
        "Складу тільки зі страв вашої бази і дам список покупок 🛒"
    )


async def run_menu_flow(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user: User,
    llm: LLMClient,
    text: str,
    intent: QueryIntent,
) -> None:
    if user.active_group_id is None:
        return
    progress = await message.answer("🧮 Складаю меню з вашої бази…")
    result, recipes = await menu_planner.plan_menu(
        session, llm, user.active_group_id, text, intent
    )
    await progress.delete()

    if not result.slots:
        await message.answer(
            result.comment
            or "Поки не можу скласти меню — у базі замало рецептів. Додайте ще 😉"
        )
        return

    slots = [s.model_dump() for s in result.slots]
    days = sorted({s["day"] for s in slots})
    await state.update_data(menu_plan={"slots": slots, "days": len(days)})

    for day in days:
        day_slots = [s for s in slots if s["day"] == day]
        is_last = day == days[-1]
        await send_long(
            message,
            render_menu_day(day, day_slots, recipes),
            reply_markup=menu_keyboard() if is_last else None,
        )
    hint = "Щоб замінити позицію, напишіть, наприклад: «заміни вечерю дня 1»."
    if result.comment:
        hint = f"ℹ️ {result.comment}\n\n{hint}"
    await message.answer(hint)


@router.callback_query(MenuCB.filter(F.action == "shop"))
async def send_shopping_list(
    query: CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    data = await state.get_data()
    plan = data.get("menu_plan")
    await query.answer()
    if not plan or not isinstance(query.message, Message):
        if isinstance(query.message, Message):
            await query.message.answer("Активного меню немає — складіть нове.")
        return
    ingredient_lists = []
    for slot in plan["slots"]:
        recipe = await repo.get_recipe(session, slot["recipe_id"])
        if recipe:
            ingredient_lists.append(recipe.ingredients)
    lines = shopping_list.aggregate(ingredient_lists)
    if not lines:
        await query.message.answer("У рецептах меню немає інгредієнтів 🤷")
        return
    await send_long(
        query.message, render_shopping_list(lines, plan.get("days", 1))
    )


@router.callback_query(MenuCB.filter(F.action == "take"))
async def take_menu(
    query: CallbackQuery, state: FSMContext, session: AsyncSession, user: User
) -> None:
    data = await state.get_data()
    plan = data.get("menu_plan")
    if not plan or user.active_group_id is None:
        await query.answer("Активного меню немає", show_alert=True)
        return
    for slot in plan["slots"]:
        await repo.record_serve(
            session,
            group_id=user.active_group_id,
            recipe_id=slot["recipe_id"],
            user_id=user.tg_user_id,
            meal_type=slot["meal"],
            served_on=date.today(),
        )
    await query.answer("Меню зафіксовано — ці страви не повторюватиму тиждень 👍")


async def run_replace_flow(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user: User,
    llm: LLMClient,
    text: str,
    intent: QueryIntent,
) -> None:
    data = await state.get_data()
    plan = data.get("menu_plan")
    if not plan or user.active_group_id is None:
        await message.answer(
            "Активного меню немає. Спершу складіть меню, наприклад: «меню на 2 дні»."
        )
        return
    day = intent.replace_day or 1
    meal = intent.replace_meal or "dinner"
    target = next(
        (s for s in plan["slots"] if s["day"] == day and s["meal"] == meal), None
    )
    if target is None:
        await message.answer(
            f"У меню немає позиції «{MEAL_LABELS.get(meal, meal)} дня {day}»."
        )
        return

    new_id, recipes = await menu_planner.replace_slot(
        session, llm, user.active_group_id, text, intent, plan["slots"]
    )
    if new_id is None:
        await message.answer("Не знайшов, чим замінити — у базі більше немає підходящих страв.")
        return
    target["recipe_id"] = new_id
    await state.update_data(menu_plan=plan)
    day_slots = [s for s in plan["slots"] if s["day"] == day]
    for slot in day_slots:
        if slot["recipe_id"] not in recipes:
            recipe = await repo.get_recipe(session, slot["recipe_id"])
            if recipe:
                recipes[recipe.id] = recipe
    await message.answer("Готово, замінив! Оновлений день:")
    await send_long(
        message, render_menu_day(day, day_slots, recipes), reply_markup=menu_keyboard()
    )
