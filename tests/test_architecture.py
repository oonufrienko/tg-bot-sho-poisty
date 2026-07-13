"""Архітектурні тести — охороняють правила з ARCHITECTURE.md.

Якщо тест упав — виправляйте код, а не тест. Перевірки працюють через ast,
щоб не імпортувати aiogram/sqlalchemy у тестовому процесі.
"""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOT = ROOT / "bot"

# Свідомий виняток: адаптер «Telegram-повідомлення → вхід для екстракції»
SERVICES_AIOGRAM_WHITELIST = {"ingestion.py"}


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _imported_modules(tree: ast.Module) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def _imported_names_from(tree: ast.Module, module_prefix: str) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ImportFrom)
            and node.module
            and node.module.split(".")[0] == module_prefix
        ):
            names.update(alias.name for alias in node.names)
    return names


def _is_property(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(
        isinstance(d, ast.Name) and d.id == "property" for d in func.decorator_list
    )


def test_models_are_data_only():
    """Моделі — лише колонки та прості @property, без методів з логікою."""
    tree = _parse(BOT / "db" / "models.py")
    offenders = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if item.name.startswith("__") or _is_property(item):
                    continue
                offenders.append(f"{node.name}.{item.name}")
    assert not offenders, (
        f"Моделі обростають логікою: {offenders}. "
        "Перенесіть її у bot/db/repo.py або bot/services/ (ARCHITECTURE.md, п.1)."
    )


def test_models_do_not_import_upper_layers():
    modules = _imported_modules(_parse(BOT / "db" / "models.py"))
    forbidden = {
        m for m in modules
        if m.split(".")[0] == "aiogram"
        or m.startswith("bot.services")
        or m.startswith("bot.handlers")
    }
    assert not forbidden, (
        f"models.py імпортує верхні шари: {forbidden} (ARCHITECTURE.md, п.1)."
    )


def test_services_do_not_know_telegram():
    offenders = []
    for path in sorted((BOT / "services").rglob("*.py")):
        if path.name in SERVICES_AIOGRAM_WHITELIST:
            continue
        modules = _imported_modules(_parse(path))
        if any(m.split(".")[0] == "aiogram" for m in modules):
            offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, (
        f"Сервіси імпортують aiogram: {offenders}. Сервіси приймають прості типи "
        "(group_id, текст), Telegram-об'єкти лишаються у handlers (ARCHITECTURE.md, п.3)."
    )


def test_handlers_use_repo_not_raw_sql():
    """Хендлерам з sqlalchemy дозволено лише тип AsyncSession."""
    allowed = {"AsyncSession"}
    offenders = []
    for path in sorted((BOT / "handlers").rglob("*.py")):
        names = _imported_names_from(_parse(path), "sqlalchemy")
        extra = names - allowed
        if extra:
            offenders.append(f"{path.relative_to(ROOT)}: {sorted(extra)}")
    assert not offenders, (
        f"Хендлери тягнуть sqlalchemy напряму: {offenders}. "
        "Доступ до БД — лише через bot/db/repo.py (ARCHITECTURE.md, пп.2, 4)."
    )


def test_repo_is_the_only_sql_entry_point():
    sql_names = {"select", "delete", "update", "insert", "text"}
    offenders = []
    for path in sorted(BOT.rglob("*.py")):
        if path == BOT / "db" / "repo.py":
            continue
        used = _imported_names_from(_parse(path), "sqlalchemy") & sql_names
        if used:
            offenders.append(f"{path.relative_to(ROOT)}: {sorted(used)}")
    assert not offenders, (
        f"SQL-конструкції поза repo.py: {offenders} (ARCHITECTURE.md, п.2)."
    )
