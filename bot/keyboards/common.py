from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.db.models import CATEGORIES

BTN_ADD = "➕ Додати рецепт"
BTN_ASK = "🍽 Що приготувати?"
BTN_MENU = "📅 Меню"
BTN_RECENT = "🕐 Останні страви"
BTN_GROUP = "👨‍👩‍👧 Група"

MENU_BUTTONS = {BTN_ADD, BTN_ASK, BTN_MENU, BTN_RECENT, BTN_GROUP}


def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_ADD), KeyboardButton(text=BTN_ASK)],
            [KeyboardButton(text=BTN_MENU), KeyboardButton(text=BTN_RECENT)],
            [KeyboardButton(text=BTN_GROUP)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Надішліть рецепт або спитайте «що на вечерю?»",
    )


class ConfirmCB(CallbackData, prefix="rc"):
    action: str  # cat | diff | save | cancel | amend
    value: str = ""


class DishCB(CallbackData, prefix="dish"):
    action: str  # take | another | choose
    recipe_id: int = 0


class MenuCB(CallbackData, prefix="menu"):
    action: str  # shop | take


class GroupCB(CallbackData, prefix="grp"):
    action: str  # switch | create | invite | members
    group_id: int = 0


class RecentCB(CallbackData, prefix="recent"):
    kind: str  # added | served


class MoveRecipesCB(CallbackData, prefix="mv"):
    action: str  # move | skip
    from_group_id: int = 0
    to_group_id: int = 0


def move_recipes_keyboard(from_group_id: int, to_group_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Так, перенести",
                    callback_data=MoveRecipesCB(
                        action="move",
                        from_group_id=from_group_id,
                        to_group_id=to_group_id,
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="Ні, залишити",
                    callback_data=MoveRecipesCB(action="skip").pack(),
                ),
            ]
        ]
    )


def confirm_keyboard(selected: list[str], difficulty: int | None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, label in CATEGORIES.items():
        mark = "✅ " if key in selected else ""
        builder.button(text=f"{mark}{label}", callback_data=ConfirmCB(action="cat", value=key))
    builder.adjust(2, 2, 2, 1)

    stars = InlineKeyboardBuilder()
    for level in range(1, 5):
        mark = "●" if difficulty == level else "○"
        stars.button(
            text=f"{mark} {'⭐' * level}", callback_data=ConfirmCB(action="diff", value=str(level))
        )
    stars.adjust(4)

    actions = InlineKeyboardBuilder()
    actions.button(text="✅ Зберегти", callback_data=ConfirmCB(action="save"))
    actions.button(text="✏️ Доповнити", callback_data=ConfirmCB(action="amend"))
    actions.button(text="❌ Скасувати", callback_data=ConfirmCB(action="cancel"))
    actions.adjust(3)

    builder.attach(stars)
    builder.attach(actions)
    return builder.as_markup()


def dish_keyboard(recipe_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Беремо", callback_data=DishCB(action="take", recipe_id=recipe_id).pack()
                ),
                InlineKeyboardButton(
                    text="🔄 Щось інше", callback_data=DishCB(action="another").pack()
                ),
            ]
        ]
    )


def options_keyboard(options: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for recipe_id, title in options:
        builder.button(
            text=title[:60], callback_data=DishCB(action="choose", recipe_id=recipe_id)
        )
    builder.adjust(1)
    return builder.as_markup()


def menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 Список покупок", callback_data=MenuCB(action="shop").pack()
                ),
                InlineKeyboardButton(
                    text="✅ Беремо меню", callback_data=MenuCB(action="take").pack()
                ),
            ]
        ]
    )


def recent_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Додані", callback_data=RecentCB(kind="added").pack()
                ),
                InlineKeyboardButton(
                    text="Рекомендовані", callback_data=RecentCB(kind="served").pack()
                ),
            ]
        ]
    )
