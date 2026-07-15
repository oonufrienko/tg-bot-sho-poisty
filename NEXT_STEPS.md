# Експлуатація бота

Бот працює. Це шпаргалка на щодня, а не інструкція з першого запуску.

**Де він живе:** `ssh ubuntu@oracle`, каталог `~/tg-bot-sho-poisty` — це git-клон
`origin`, тому оновлення робиться через `git pull`, а не копіюванням з Mac.

## Оновити код

```bash
ssh ubuntu@oracle
cd ~/tg-bot-sho-poisty
git pull
docker compose up -d --build
docker compose logs -f bot        # має бути «Бот запущено (long polling)»; вихід — Ctrl+C
```

**`--build` обов'язковий.** Без нього `up -d` бере вже зібраний образ, і бот
мовчки працюватиме на старому коді — саме так виникає крешлуп після `git pull`.

## Змінити .env (ключі, список доступу)

```bash
nano .env                 # зберегти: Ctrl+O, Enter, Ctrl+X
docker compose up -d      # саме up -d, НЕ restart
```

**`docker compose restart` не перечитує `.env`.** Змінні з `env_file` вшиваються
в контейнер при його створенні, а `restart` піднімає той самий контейнер зі
старими значеннями. `up -d` помічає зміну і перестворює його.

## Ключі в .env

| Змінна | Навіщо |
|---|---|
| `BOT_TOKEN` | Токен від [@BotFather](https://t.me/BotFather) |
| `OPENROUTER_API_KEY` | **Основний** провайдер LLM |
| `GEMINI_API_KEY` | Запасний — вмикається, лише якщо OpenRouter не заданий |
| `OPENROUTER_MODEL` | Модель — зараз `google/gemini-3.1-flash-lite-preview` |
| `ALLOWED_USER_IDS` | Хто має доступ (див. нижче) |

Потрібен хоча б один із двох ключів LLM, інакше бот не стартує.

## Доступ

`ALLOWED_USER_IDS` — id через кому: `123456,789012`. Свій id дізнатись у
[@userinfobot](https://t.me/userinfobot).

- порожнє — не пускає нікого (безпечно за замовчуванням);
- `*` — **відкриває бота всім у Telegram**, хто знайде його за іменем.

Після зміни — `docker compose up -d` (не `restart`, див. вище).

## Щоденні команди

```bash
docker compose logs -f bot                        # логи
docker compose logs bot | tail -30                # останнє, без стеження
docker compose down                               # зупинити
cp data/bot.db ~/backup-recipes-$(date +%F).db    # бекап бази рецептів
```

## Якщо щось не так

- **Бот не відповідає** → `docker compose logs bot | tail -30`.
  «Unauthorized» — невірний `BOT_TOKEN`; помилки 401/429 — ключ LLM.
- **«Це приватний сімейний бот»** → вашого id немає в `ALLOWED_USER_IDS`,
  або після зміни зробили `restart` замість `up -d`.
- **Бот на старому коді після `git pull`** → забули `--build`.
- **Кода немає в логах взагалі** → лог обривається одразу після міграцій?
  Такого більше не має бути, але саме так виглядав баг, коли alembic збивав
  root-логер на WARN.

## Про сервер

На цій же машині крутяться чужі контейнери — `tg-news-filter` і `my-tg-bot`.
Не чіпати: `docker system prune -a` та подібне знесе і їх.
