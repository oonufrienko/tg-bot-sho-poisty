import json
from html import escape

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import repo
from bot.db.models import User
from bot.keyboards.common import BTN_ADD, ConfirmCB, confirm_keyboard
from bot.rendering import render_extraction_card, render_recipe
from bot.services.ingestion import RecipeInput, collect_input
from bot.services.llm.base import LLMClient, LLMError, LLMQuotaError, RecipeExtraction
from bot.utils import send_long

router = Router(name="add_recipe")

MIME_BY_TYPE = {"photo": "image/jpeg", "pdf": "application/pdf"}


class AddStates(StatesGroup):
    confirming = State()
    amending = State()


@router.message(F.text == BTN_ADD)
async def add_hint(message: Message) -> None:
    await message.answer(
        "Надішліть рецепт у будь-якому вигляді:\n"
        "📷 фото або скріншот\n"
        "📄 PDF-файл\n"
        "✍️ текст\n"
        "↪️ або перешліть пост з каналу\n\n"
        "Я розпізнаю і запропоную зберегти 😉"
    )


async def start_recipe_flow(
    message: Message,
    state: FSMContext,
    llm: LLMClient,
    recipe_input: RecipeInput,
) -> None:
    """Спільний вхід: екстракція + картка підтвердження."""
    progress = await message.answer("🔍 Розпізнаю рецепт…")
    try:
        extraction = await llm.extract_recipe(recipe_input.text, recipe_input.files)
    except LLMQuotaError:
        await progress.edit_text(
            "Перевищено ліміт запитів AI 🕐 Зачекайте хвилину і спробуйте ще раз."
        )
        return
    except LLMError:
        await progress.edit_text(
            "Не вдалося розпізнати — сервіс AI зараз недоступний. Спробуйте ще раз за хвилину."
        )
        return
    await progress.delete()

    if not extraction.is_recipe:
        await message.answer(
            "Це не схоже на рецепт 🤔 Якщо я помиляюсь — надішліть ще раз, "
            "додавши підпис, наприклад: «збережи цей рецепт»."
        )
        return

    await show_confirmation(message, state, extraction, recipe_input)


async def show_confirmation(
    message: Message,
    state: FSMContext,
    extraction: RecipeExtraction,
    recipe_input: RecipeInput,
    edit_id: int | None = None,
) -> None:
    categories = list(extraction.suggested_categories) or ["general"]

    await state.set_state(AddStates.confirming)
    await state.update_data(
        extraction=extraction.model_dump(),
        cats=categories,
        diff=extraction.difficulty,
        source_type=recipe_input.source_type,
        media=recipe_input.media,
        orig_text=recipe_input.text,
        dup_ok=False,  # нова картка — перевірка дубліката спрацює заново
        # Задаємо завжди: update_data зливає, тож без цього edit_id від
        # покинутого редагування прилип би і «Зберегти» переписало б чужий рецепт.
        edit_id=edit_id,
    )
    card = render_extraction_card(
        extraction.title,
        [i.model_dump() for i in extraction.ingredients],
        extraction.steps,
        extraction.calories,
        extraction.missing_info,
    )
    await send_long(
        message, card, reply_markup=confirm_keyboard(categories, extraction.difficulty)
    )


@router.message(F.photo | F.document)
async def handle_media(
    message: Message, state: FSMContext, bot: Bot, llm: LLMClient
) -> None:
    recipe_input = await collect_input(message, bot)
    if recipe_input.error:
        await message.answer(recipe_input.error)
        return
    await start_recipe_flow(message, state, llm, recipe_input)


@router.callback_query(AddStates.confirming, ConfirmCB.filter(F.action == "cat"))
async def toggle_category(
    query: CallbackQuery, callback_data: ConfirmCB, state: FSMContext
) -> None:
    data = await state.get_data()
    cats: list[str] = data.get("cats", [])
    if callback_data.value in cats:
        cats = [c for c in cats if c != callback_data.value]
    else:
        cats = cats + [callback_data.value]
    await state.update_data(cats=cats)
    await query.answer()
    if isinstance(query.message, Message):
        await query.message.edit_reply_markup(
            reply_markup=confirm_keyboard(cats, data.get("diff"))
        )


@router.callback_query(AddStates.confirming, ConfirmCB.filter(F.action == "diff"))
async def set_difficulty(
    query: CallbackQuery, callback_data: ConfirmCB, state: FSMContext
) -> None:
    data = await state.get_data()
    diff = int(callback_data.value)
    await state.update_data(diff=diff)
    await query.answer()
    if isinstance(query.message, Message):
        await query.message.edit_reply_markup(
            reply_markup=confirm_keyboard(data.get("cats", []), diff)
        )


@router.callback_query(AddStates.confirming, ConfirmCB.filter(F.action == "cancel"))
async def cancel(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await query.answer("Скасовано")
    if isinstance(query.message, Message):
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.answer("Добре, не зберігаю 👌")


@router.callback_query(AddStates.confirming, ConfirmCB.filter(F.action == "amend"))
async def amend_start(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AddStates.amending)
    await query.answer()
    if isinstance(query.message, Message):
        await query.message.answer(
            "Надішліть уточнення текстом — назву, інгредієнти, кроки чи виправлення. "
            "Я оновлю картку."
        )


@router.message(AddStates.amending, F.text)
async def amend_apply(
    message: Message, state: FSMContext, bot: Bot, llm: LLMClient
) -> None:
    data = await state.get_data()
    files: list[tuple[bytes, str]] = []
    for file_id, media_type in data.get("media", []):
        buffer = await bot.download(file_id)
        if buffer:
            files.append((buffer.read(), MIME_BY_TYPE.get(media_type, "image/jpeg")))

    previous = json.dumps(data.get("extraction", {}), ensure_ascii=False)
    merged_text = (
        f"Попередній розбір рецепта (JSON): {previous}\n"
        f"Оригінальний текст: {data.get('orig_text') or '—'}\n"
        f"КОРИСТУВАЧ ДОПОВНИВ/ВИПРАВИВ: {message.text}\n"
        "Онови структуру рецепта з урахуванням доповнення користувача. "
        "Доповнення користувача має пріоритет."
    )
    recipe_input = RecipeInput(
        text=data.get("orig_text"),
        files=files,
        media=[tuple(m) for m in data.get("media", [])],
        source_type=data.get("source_type", "text"),
    )
    recipe_input.text = merged_text
    progress = await message.answer("🔄 Оновлюю…")
    try:
        extraction = await llm.extract_recipe(merged_text, files)
    except LLMQuotaError:
        await progress.edit_text(
            "Перевищено ліміт запитів AI 🕐 Зачекайте хвилину і спробуйте ще раз."
        )
        return
    except LLMError:
        await progress.edit_text("Сервіс AI недоступний, спробуйте за хвилину.")
        return
    await progress.delete()
    recipe_input.text = data.get("orig_text")
    extraction.is_recipe = True
    # Якщо «Доповнити» натиснули під час редагування — лишаємось у режимі правки.
    await show_confirmation(
        message, state, extraction, recipe_input, edit_id=data.get("edit_id")
    )


@router.callback_query(AddStates.confirming, ConfirmCB.filter(F.action == "save"))
async def save_recipe(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    data = await state.get_data()
    extraction = data.get("extraction", {})
    title = (extraction.get("title") or "").strip()
    ingredients = extraction.get("ingredients") or []
    steps = (extraction.get("steps") or "").strip()

    if not title:
        await query.answer(
            "Немає назви страви. Натисніть «✏️ Доповнити» і надішліть назву.",
            show_alert=True,
        )
        return
    if not ingredients and not steps:
        await query.answer(
            "Не розпізнано ні інгредієнтів, ні кроків. Натисніть «✏️ Доповнити».",
            show_alert=True,
        )
        return
    if user.active_group_id is None:
        await query.answer("Немає активної групи", show_alert=True)
        return

    edit_id = data.get("edit_id")
    if edit_id:
        updated = await repo.update_recipe(
            session,
            edit_id,
            user.active_group_id,
            title=title,
            ingredients=ingredients,
            steps=steps,
            categories=data.get("cats") or ["general"],
            difficulty=data.get("diff"),
            calories=extraction.get("calories"),
        )
        if updated is None:
            await query.answer(
                "Рецепт уже видалено або він з іншої групи.", show_alert=True
            )
            return
        await state.clear()
        await query.answer("Оновлено!")
        if isinstance(query.message, Message):
            await query.message.edit_reply_markup(reply_markup=None)
            await send_long(
                query.message, "✅ Оновлено:\n\n" + render_recipe(updated)
            )
        return

    # Перевірка дубліката лише для нового рецепта: правка завжди «знайшла б» саму себе.
    existing = await repo.find_recipe_by_title(session, user.active_group_id, title)
    if existing is not None and not data.get("dup_ok"):
        await state.update_data(dup_ok=True)
        await query.answer()
        if isinstance(query.message, Message):
            await query.message.answer(
                f"У базі вже є рецепт «{escape(existing.title)}» 🤔 Зберегти копію?",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="✅ Зберегти все одно",
                                callback_data=ConfirmCB(action="save").pack(),
                            ),
                            InlineKeyboardButton(
                                text="❌ Скасувати",
                                callback_data=ConfirmCB(action="cancel").pack(),
                            ),
                        ]
                    ]
                ),
            )
        return

    recipe = await repo.add_recipe(
        session,
        group_id=user.active_group_id,
        added_by=user.tg_user_id,
        title=title,
        ingredients=ingredients,
        steps=steps,
        categories=data.get("cats") or ["general"],
        difficulty=data.get("diff"),
        calories=extraction.get("calories"),
        source_type=data.get("source_type", "text"),
        original_text=data.get("orig_text"),
        media=[tuple(m) for m in data.get("media", [])],
    )
    await state.clear()
    await query.answer("Збережено!")
    if isinstance(query.message, Message):
        await query.message.edit_reply_markup(reply_markup=None)
        await send_long(query.message, "✅ Додано до бази:\n\n" + render_recipe(recipe))
