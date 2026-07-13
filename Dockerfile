FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY bot ./bot
COPY alembic.ini ./
COPY alembic ./alembic

RUN pip install --no-cache-dir .

CMD ["python", "-m", "bot.main"]
