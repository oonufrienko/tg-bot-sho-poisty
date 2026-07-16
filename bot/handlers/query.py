from datetime import date
from html import escape

import json

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.chat_action import ChatActionSender
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import repo
from bot.db.models import MEAL_LABELS, User
from bot.handlers.add_recipe import show_confirmation, start_recipe_flow
from bot.handlers.menu import run_menu_flow, run_replace_flow
from bot.handlers.start import HELP
from bot.keyboards.common import (
    BTN_ASK,
    BTN_MY_RECIPES,
    AskCB,
    DishCB,
    ListActionCB,
    RecentCB,
    ask_keyboard,
    cancel_number_keyboard,
    delete_confirm_keyboard,
    dish_keyboard,
    list_actions_keyboard,
    options_keyboard,
    recent_keyboard,
)
from bot.rendering import render_recipe, render_recipe_list
from bot.services import retrieval
from bot.services.ingestion import RecipeInput, collect_input
from bot.services.llm.base import LLMClient, LLMError, LLMQuotaError, QueryIntent
from bot.utils import send_long

router = Router(name="query")

AI_UNAVAILABLE = "Сервіс AI зараз недоступний, спробуйте за хвилину 🙏"
AI_RATE_LIMITED = "Перевищено ліміт запитів AI 🕐 Зачекайте хвилину і спробуйте ще раз."
FOREIGN_RECIPE = "Ця страва з іншої групи — ви переключились. Спитайте мене заново 🙂"
LIST_GONE = "Спочатку відкрийте «📖 Мої рецепти» → «Весь список» 🙂"


class ListStates(StatesGroup):
    deleting = State()  # чекаємо номер для видалення
    choosing_edit = State()  # чекаємо номер для редагування
    editing = State()  # чекаємо текст правки


def _pick_by_number(text: str, ids: list[int]) -> int | None:
    """Номер зі списку → recipe_id. None, якщо це не номер або він поза списком."""
    raw = (text or "").strip().rstrip(".")
    if not raw.isdigit():
        return None
    number = int(raw)
    if not 1 <= number <= len(ids):
        return None
    return ids[number - 1]


# Готові підказки: key → (напис на кнопці, запит, інтент).
# Інтент відомий наперед, тому кнопка не витрачає зайвий раунд на route_query.
ASK_SUGGESTIONS: dict[str, tuple[str, str, dict]] = {
    "breakfast": ("Сніданок", "сніданок", {"intent": "find_dish", "meal_types": ["breakfast"]}),
    "dinner": ("Вечеря", "вечеря", {"intent": "find_dish", "meal_types": ["dinner"]}),
    "dessert": ("Десерт", "десерт", {"intent": "find_dish", "meal_types": ["dessert"]}),
    "tea": ("До чаю", "щось до чаю", {"intent": "find_dish", "meal_types": ["dessert"]}),
    "menu2": ("Меню на 2 дні", "меню на 2 дні", {"intent": "plan_menu", "days": 2}),
}


@router.message(F.text == BTN_ASK)
async def ask_hint(message: Message) -> None:
    await message.answer(
        "Що шукаємо?\n\nАбо просто напишіть своїми словами — наприклад, «що приготувати з курки?»",
        reply_markup=ask_keyboard([(key, label) for key, (label, _, _) in ASK_SUGGESTIONS.items()]),
    )


@router.callback_query(AskCB.filter())
async def ask_suggestion(
    query: CallbackQuery,
    callback_data: AskCB,
    state: FSMContext,
    session: AsyncSession,
    user: User,
    llm: LLMClient,
    bot: Bot,
) -> None:
    await query.answer()
    suggestion = ASK_SUGGESTIONS.get(callback_data.key)
    if suggestion is None or not isinstance(query.message, Message):
        return
    _, text, payload = suggestion
    intent = QueryIntent.model_validate(payload)
    try:
        async with ChatActionSender.typing(bot=bot, chat_id=query.message.chat.id):
            if intent.intent == "plan_menu":
                await run_menu_flow(query.message, state, session, user, llm, text, intent)
            else:
                await run_find_dish(query.message, state, session, user, llm, text, intent)
    except LLMQuotaError:
        await query.message.answer(AI_RATE_LIMITED)
    except LLMError:
        await query.message.answer(AI_UNAVAILABLE)


@router.message(F.text == BTN_MY_RECIPES)
async def recent_hint(message: Message) -> None:
    await message.answer("Що показати?", reply_markup=recent_keyboard())


@router.callback_query(RecentCB.filter())
async def recent_list(
    query: CallbackQuery,
    callback_data: RecentCB,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    await query.answer()
    if user.active_group_id is None or not isinstance(query.message, Message):
        return
    if callback_data.kind == "all":
        recipes = await repo.group_recipes(session, user.active_group_id)
        if not recipes:
            await query.message.answer("У базі поки немає рецептів.")
            return
        text, ids = render_recipe_list(recipes)
        # Номери живуть у стані: користувач вводить їх, а не recipe_id.
        await state.set_state(None)
        await state.update_data(list_ids=ids)
        await send_long(query.message, text, reply_markup=list_actions_keyboard())
        return
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
    await state.update_data(
        q_text=text, q_intent=intent.model_dump(), q_group_id=user.active_group_id
    )

    if selection.need_clarification and selection.option_ids:
        options = [(i, by_id[i].title) for i in selection.option_ids]
        await state.update_data(q_shown=list(exclude_ids))
        await message.answer(
            escape(selection.clarification_question or "Оберіть варіант:"),
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
    recipe = await repo.get_recipe(session, callback_data.recipe_id, user.active_group_id)
    if recipe is None:
        await query.answer(FOREIGN_RECIPE, show_alert=True)
        return
    data = await state.get_data()
    intent = QueryIntent.model_validate(data["q_intent"]) if data.get("q_intent") else None
    await repo.record_serve(
        session,
        group_id=user.active_group_id,
        recipe_id=recipe.id,
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
    bot: Bot,
) -> None:
    await query.answer()
    if not isinstance(query.message, Message):
        return
    data = await state.get_data()
    if not data.get("q_text") or data.get("q_group_id") != user.active_group_id:
        await query.message.answer("Спитайте мене заново, що підібрати 🙂")
        return
    intent = QueryIntent.model_validate(data["q_intent"])
    try:
        async with ChatActionSender.typing(bot=bot, chat_id=query.message.chat.id):
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
    except LLMQuotaError:
        await query.message.answer(AI_RATE_LIMITED)
    except LLMError:
        await query.message.answer(AI_UNAVAILABLE)


@router.callback_query(DishCB.filter(F.action == "choose"))
async def choose_dish(
    query: CallbackQuery,
    callback_data: DishCB,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    if not isinstance(query.message, Message) or user.active_group_id is None:
        await query.answer()
        return
    recipe = await repo.get_recipe(session, callback_data.recipe_id, user.active_group_id)
    if recipe is None:
        await query.answer(FOREIGN_RECIPE, show_alert=True)
        return
    await query.answer()
    data = await state.get_data()
    shown = data.get("q_shown", []) + [recipe.id]
    await show_dish(query.message, state, recipe, shown)


async def _ask_number(
    query: CallbackQuery, state: FSMContext, target: State, prompt: str
) -> None:
    await query.answer()
    if not isinstance(query.message, Message):
        return
    data = await state.get_data()
    if not data.get("list_ids"):
        await query.message.answer(LIST_GONE)
        return
    await state.set_state(target)
    await query.message.answer(prompt, reply_markup=cancel_number_keyboard())


@router.callback_query(ListActionCB.filter(F.action == "del"))
async def ask_delete_number(query: CallbackQuery, state: FSMContext) -> None:
    await _ask_number(
        query,
        state,
        ListStates.deleting,
        "Введіть номер страви зі списку, яку треба видалити:",
    )


@router.callback_query(ListActionCB.filter(F.action == "edit"))
async def ask_edit_number(query: CallbackQuery, state: FSMContext) -> None:
    await _ask_number(
        query,
        state,
        ListStates.choosing_edit,
        "Введіть номер страви зі списку, яку треба відредагувати:",
    )


@router.callback_query(ListActionCB.filter(F.action == "cancel"))
async def cancel_number(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(None)
    await query.answer("Скасовано")
    if isinstance(query.message, Message):
        await query.message.edit_reply_markup(reply_markup=None)


async def _resolve_number(
    message: Message, state: FSMContext, session: AsyncSession, user: User
):
    """Спільне для видалення й редагування: номер → рецепт, або None + підказка."""
    data = await state.get_data()
    ids: list[int] = data.get("list_ids") or []
    if not ids or user.active_group_id is None:
        await state.set_state(None)
        await message.answer(LIST_GONE)
        return None
    recipe_id = _pick_by_number(message.text or "", ids)
    if recipe_id is None:
        await message.answer(
            f"Потрібен номер від 1 до {len(ids)}. Спробуйте ще раз:",
            reply_markup=cancel_number_keyboard(),
        )
        return None
    recipe = await repo.get_recipe(session, recipe_id, user.active_group_id)
    if recipe is None:
        await state.set_state(None)
        await message.answer(LIST_GONE)
        return None
    return recipe


@router.message(ListStates.deleting, F.text)
async def delete_by_number(
    message: Message, state: FSMContext, session: AsyncSession, user: User
) -> None:
    recipe = await _resolve_number(message, state, session, user)
    if recipe is None:
        return
    await state.set_state(None)
    await message.answer(
        f"Видалити «{escape(recipe.title)}» з бази?\nДію не можна скасувати.",
        reply_markup=delete_confirm_keyboard(recipe.id),
    )


@router.message(ListStates.choosing_edit, F.text)
async def show_for_edit(
    message: Message, state: FSMContext, session: AsyncSession, user: User
) -> None:
    recipe = await _resolve_number(message, state, session, user)
    if recipe is None:
        return
    await state.set_state(ListStates.editing)
    await state.update_data(edit_id=recipe.id)
    await send_long(
        message,
        render_recipe(recipe)
        + "\n\n✏️ Надішліть текстом, що змінити або додати — наприклад "
        "«додай 200г сиру» чи «заміни крок 3 на: випікати 40хв».",
        reply_markup=cancel_number_keyboard(),
    )


@router.message(ListStates.editing, F.text)
async def apply_edit(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user: User,
    llm: LLMClient,
    bot: Bot,
) -> None:
    data = await state.get_data()
    if user.active_group_id is None:
        return
    recipe = await repo.get_recipe(session, data.get("edit_id", 0), user.active_group_id)
    if recipe is None:
        await state.set_state(None)
        await message.answer(LIST_GONE)
        return

    current = json.dumps(
        {
            "title": recipe.title,
            "ingredients": recipe.ingredients,
            "steps": recipe.steps,
            "calories": recipe.calories,
        },
        ensure_ascii=False,
    )
    merged_text = (
        f"Поточний рецепт (JSON): {current}\n"
        f"КОРИСТУВАЧ ЗМІНЮЄ/ДОПОВНЮЄ: {message.text}\n"
        "Онови структуру рецепта з урахуванням правки. Правка користувача має "
        "пріоритет; решту полів залиш як є."
    )
    try:
        async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
            extraction = await llm.extract_recipe(merged_text, [])
    except LLMQuotaError:
        await message.answer(AI_RATE_LIMITED)
        return
    except LLMError:
        await message.answer(AI_UNAVAILABLE)
        return

    # Той самий прийом, що і в amend_apply: правимо екстракцію перед карткою.
    extraction.is_recipe = True
    extraction.suggested_categories = recipe.category_keys or extraction.suggested_categories
    if extraction.difficulty is None:
        extraction.difficulty = recipe.difficulty
    recipe_input = RecipeInput(
        text=recipe.original_text,
        files=[],
        media=[],
        source_type=recipe.source_type,
    )
    # edit_id передаємо явно: save_recipe за ним піде в update, а не в add.
    await show_confirmation(message, state, extraction, recipe_input, edit_id=recipe.id)


@router.callback_query(DishCB.filter(F.action == "del_ok"))
async def confirm_delete(
    query: CallbackQuery,
    callback_data: DishCB,
    session: AsyncSession,
    user: User,
) -> None:
    if user.active_group_id is None:
        await query.answer()
        return
    title = await repo.delete_recipe(
        session, callback_data.recipe_id, user.active_group_id
    )
    if title is None:
        await query.answer(FOREIGN_RECIPE, show_alert=True)
        return
    await query.answer("Видалено")
    if isinstance(query.message, Message):
        await query.message.edit_text(f"🗑 Видалено «{escape(title)}»")


@router.callback_query(DishCB.filter(F.action == "del_no"))
async def cancel_delete(query: CallbackQuery) -> None:
    await query.answer()
    if isinstance(query.message, Message):
        await query.message.edit_text("Добре, залишаю 👌")


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
        async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
            intent = await llm.route_query(text)

            match intent.intent:
                case "add_recipe":
                    recipe_input = await collect_input(message, bot)
                    await start_recipe_flow(message, state, llm, recipe_input)
                case "find_dish":
                    await run_find_dish(message, state, session, user, llm, text, intent)
                case "another_suggestion":
                    data = await state.get_data()
                    if data.get("q_text") and data.get("q_group_id") == user.active_group_id:
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
    except LLMQuotaError:
        await message.answer(AI_RATE_LIMITED)
    except LLMError:
        await message.answer(AI_UNAVAILABLE)
