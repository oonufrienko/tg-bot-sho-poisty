#!/usr/bin/env python3
"""Одноразово приводить назви рецептів у базі до єдиного стилю.

Нові рецепти нормалізуються під час розпізнавання (bot/services/titles.py);
цей скрипт наздоганяє те, що вже лежить у базі.

    uv run python scripts/normalize_titles.py            # dry-run, нічого не пише
    uv run python scripts/normalize_titles.py --apply    # оновлює базу

Перед --apply зробіть бекап: ~/backup-script/backup.sh (див. RUNBOOK.md).
"""

import argparse
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot.services.titles import normalize_title  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="data/bot.db", help="шлях до бази")
    parser.add_argument("--apply", action="store_true", help="записати зміни")
    args = parser.parse_args()

    connection = sqlite3.connect(args.db)
    rows = connection.execute("SELECT id, title FROM recipes ORDER BY id").fetchall()
    changes = [
        (recipe_id, title, normalize_title(title))
        for recipe_id, title in rows
        if normalize_title(title) != title
    ]

    for recipe_id, before, after in changes:
        print(f"{recipe_id:>5} | {before} → {after}")

    if args.apply and changes:
        connection.executemany(
            "UPDATE recipes SET title = ? WHERE id = ?",
            [(after, recipe_id) for recipe_id, _, after in changes],
        )
        connection.commit()

    verb = "оновлено" if args.apply else "буде оновлено"
    print(f"\n{len(changes)} з {len(rows)} назв {verb}.")
    if changes and not args.apply:
        print("Запустіть з --apply, щоб записати.")
    connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
