from bot.services.shopping_list import aggregate, parse_qty


def test_parse_qty_variants():
    assert parse_qty("2") == 2.0
    assert parse_qty("1,5") == 1.5
    assert parse_qty("1.5") == 1.5
    assert parse_qty("1/2") == 0.5
    assert parse_qty("2-3") == 3.0
    assert parse_qty("по смаку") is None
    assert parse_qty(None) is None
    assert parse_qty("") is None


def test_aggregate_sums_same_ingredient_and_unit():
    lists = [
        [{"name": "Курка", "qty": "500", "unit": "г"}],
        [{"name": "курка", "qty": "1000", "unit": "г"}],
    ]
    lines = aggregate(lists)
    assert lines == ["Курка — 1500 г"]


def test_aggregate_keeps_different_units_separate():
    lists = [
        [{"name": "молоко", "qty": "1", "unit": "л"}],
        [{"name": "молоко", "qty": "200", "unit": "мл"}],
    ]
    lines = aggregate(lists)
    assert len(lines) == 2


def test_aggregate_decimal_comma_output():
    lists = [
        [{"name": "борошно", "qty": "1,5", "unit": "скл"}],
        [{"name": "борошно", "qty": "1", "unit": "скл"}],
    ]
    assert aggregate(lists) == ["борошно — 2,5 скл"]


def test_aggregate_unparsed_qty_becomes_note():
    lists = [
        [{"name": "сіль", "qty": "по смаку", "unit": None}],
        [{"name": "олія", "qty": "2", "unit": "ст.л"}],
    ]
    lines = aggregate(lists)
    assert "олія — 2 ст.л" in lines
    assert "сіль — по смаку" in lines


def test_aggregate_mixed_parsed_and_note_for_same_name():
    lists = [
        [{"name": "цукор", "qty": "100", "unit": "г"}],
        [{"name": "цукор", "qty": "за смаком", "unit": None}],
    ]
    lines = aggregate(lists)
    assert lines == ["цукор — 100 г (+ за смаком)"]
