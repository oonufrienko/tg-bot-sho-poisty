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


def _is_trivial_property(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Просте read-only property: (docstring +) один return, без присвоєнь/await."""
    if isinstance(func, ast.AsyncFunctionDef):
        return False
    body = list(func.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
        body = body[1:]  # docstring
    if len(body) != 1 or not isinstance(body[0], ast.Return):
        return False
    return not any(isinstance(n, ast.Await) for n in ast.walk(body[0]))


ALLOWED_MODEL_DUNDERS = {"__repr__", "__str__"}


def test_models_are_data_only():
    """Моделі — лише колонки та прості read-only @property, без методів з логікою."""
    tree = _parse(BOT / "db" / "models.py")
    offenders = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        for item in node.body:
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if item.name.startswith("__") and item.name in ALLOWED_MODEL_DUNDERS:
                continue
            if _is_property(item) and _is_trivial_property(item):
                continue
            offenders.append(f"{node.name}.{item.name}")
    assert not offenders, (
        f"Моделі обростають логікою: {offenders}. Дозволені лише прості read-only "
        "@property (один return) та __repr__/__str__. Логіку перенесіть у "
        "bot/db/repo.py або bot/services/ (ARCHITECTURE.md, п.1)."
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
    # Пласкі імена + проксі-модулі, через які можна дістати ті самі конструкції
    sql_names = {"select", "delete", "update", "insert", "text", "sql", "orm", "expression"}
    offenders = []
    for path in sorted(BOT.rglob("*.py")):
        if path == BOT / "db" / "repo.py":
            continue
        tree = _parse(path)
        used = _imported_names_from(tree, "sqlalchemy") & sql_names
        if used:
            offenders.append(f"{path.relative_to(ROOT)}: {sorted(used)}")
        # `import sqlalchemy as sa` дає доступ до sa.select(...) в обхід перевірки
        module_imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
            if alias.name.split(".")[0] == "sqlalchemy"
        }
        if module_imports:
            offenders.append(
                f"{path.relative_to(ROOT)}: import {sorted(module_imports)} "
                "(використовуйте точкові from-імпорти, SQL — лише в repo.py)"
            )
    assert not offenders, (
        f"SQL-конструкції поза repo.py: {offenders} (ARCHITECTURE.md, п.2)."
    )
