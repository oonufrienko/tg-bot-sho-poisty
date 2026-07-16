import pytest

from bot.handlers.query import _pick_by_number

IDS = [11, 22, 33]


@pytest.mark.parametrize(
    "text, expected",
    [
        ("1", 11),
        ("3", 33),
        ("  2  ", 22),  # користувачі лишають пробіли
        ("2.", 22),  # і копіюють номер разом із крапкою зі списку
        ("0", None),  # список нумерується з 1
        ("4", None),  # за межами списку
        ("-1", None),
        ("два", None),
        ("", None),
        ("1 2", None),
    ],
)
def test_pick_by_number(text, expected):
    assert _pick_by_number(text, IDS) == expected


def test_pick_by_number_on_empty_list():
    assert _pick_by_number("1", []) is None
