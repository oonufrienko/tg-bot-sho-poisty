# tg-bot-sho-poisty

Сімейний Telegram-бот з базою рецептів (Python 3.12, aiogram 3, SQLite, Gemini).

- **Обов'язково дотримуйся правил шарів з [ARCHITECTURE.md](ARCHITECTURE.md).**
  Вони перевіряються тестами в `tests/test_architecture.py` — тести мають
  лишатися зеленими; якщо впали — виправляй код, не тест.
- Тести: `uv run pytest`. Запуск: `uv run python -m bot.main` (потрібен `.env`).
- Деплой: сервер `ssh ubuntu@oracle`, каталог `~/tg-bot-sho-poisty`, `docker compose up -d --build`.
