from bot.handlers.query import ASK_SUGGESTIONS
from bot.keyboards.common import AskCB, ask_keyboard
from bot.services.llm.base import QueryIntent


def test_every_suggestion_builds_a_valid_intent():
    """Інтенти задані діктами, тож помилку в ключі категорії видно лише тут."""
    for key, (label, text, payload) in ASK_SUGGESTIONS.items():
        intent = QueryIntent.model_validate(payload)
        assert label and text, key
        assert intent.intent in {"find_dish", "plan_menu"}, key


def test_keyboard_callbacks_resolve_back_to_suggestions():
    markup = ask_keyboard([(k, v[0]) for k, v in ASK_SUGGESTIONS.items()])
    buttons = [b for row in markup.inline_keyboard for b in row]
    assert len(buttons) == len(ASK_SUGGESTIONS)
    for button in buttons:
        # 64 байти — ліміт Telegram на callback_data
        assert len(button.callback_data.encode()) <= 64
        assert AskCB.unpack(button.callback_data).key in ASK_SUGGESTIONS
