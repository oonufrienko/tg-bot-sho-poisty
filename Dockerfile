FROM python:3.12-slim

WORKDIR /app

# Шар 1: лише залежності. Кешується, поки не зміниться pyproject.toml.
# Стаб bot/__init__.py потрібен, бо packages.find вимагає існування пакета.
COPY pyproject.toml README.md ./
RUN mkdir -p bot && touch bot/__init__.py \
 && pip install --no-cache-dir . \
 && rm -rf bot

# Шар 2: код. Змінюється часто, тому ставимо його окремо і без мережі.
COPY bot ./bot
COPY alembic.ini ./
COPY alembic ./alembic
RUN pip install --no-cache-dir --no-deps .

CMD ["python", "-m", "bot.main"]
