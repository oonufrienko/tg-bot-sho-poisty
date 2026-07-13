"""Агрегація інгредієнтів у список покупок."""

import re
from collections import defaultdict

_NUMBER = re.compile(r"^\s*(\d+(?:[.,]\d+)?)\s*$")
_FRACTION = re.compile(r"^\s*(\d+)\s*/\s*(\d+)\s*$")
_RANGE = re.compile(r"^\s*(\d+(?:[.,]\d+)?)\s*[-–]\s*(\d+(?:[.,]\d+)?)\s*$")


def parse_qty(qty: str | None) -> float | None:
    """«1,5» → 1.5; «1/2» → 0.5; «2-3» → 3 (беремо більше, щоб точно вистачило)."""
    if not qty:
        return None
    if match := _NUMBER.match(qty):
        return float(match.group(1).replace(",", "."))
    if match := _FRACTION.match(qty):
        return float(match.group(1)) / float(match.group(2))
    if match := _RANGE.match(qty):
        return float(match.group(2).replace(",", "."))
    return None


def _format_amount(value: float) -> str:
    return f"{value:g}".replace(".", ",")


def aggregate(ingredient_lists: list[list[dict]]) -> list[str]:
    """Сумує кількості за (назва, одиниця). Повертає готові рядки списку покупок."""
    sums: dict[tuple[str, str], float] = defaultdict(float)
    labels: dict[tuple[str, str], str] = {}
    unparsed: dict[str, list[str]] = defaultdict(list)

    for ingredients in ingredient_lists:
        for item in ingredients:
            name = (item.get("name") or "").strip()
            if not name:
                continue
            qty = parse_qty(item.get("qty"))
            unit = (item.get("unit") or "").strip()
            key = (name.lower(), unit.lower())
            if qty is not None:
                sums[key] += qty
                labels.setdefault(key, name)
            else:
                note = (item.get("qty") or "").strip()
                if note and note not in unparsed[name.lower()]:
                    unparsed[name.lower()].append(note)
                unparsed.setdefault(name.lower(), [])
                labels.setdefault((name.lower(), ""), name)

    lines: list[str] = []
    seen_names: set[str] = set()
    for (name_key, unit_key), total in sorted(sums.items()):
        name = labels[(name_key, unit_key)]
        unit = f" {unit_key}" if unit_key else ""
        line = f"{name} — {_format_amount(total)}{unit}"
        extra_notes = unparsed.pop(name_key, [])
        if extra_notes:
            line += f" (+ {', '.join(extra_notes)})"
        lines.append(line)
        seen_names.add(name_key)

    for name_key, notes in sorted(unparsed.items()):
        if name_key in seen_names:
            continue
        name = labels.get((name_key, ""), name_key)
        lines.append(f"{name} — {', '.join(notes)}" if notes else name)
    return lines
