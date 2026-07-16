# Експлуатація бота

Бот працює. Це шпаргалка на щодня, а не інструкція з першого запуску.

**Де він живе:** `ssh ubuntu@oracle`, каталог `~/tg-bot-sho-poisty` — це git-клон
`origin`, тому оновлення робиться через `git pull`, а не копіюванням з Mac.

## Оновити код

**Само собою:** мерж PR у `main` запускає тести й деплой — GitHub Actions
заходить по SSH і виконує `scripts/deploy.sh` (git pull + rebuild). Статус —
вкладка Actions на GitHub. Хвилини за 2–3 після мержу бот уже на новому коді.

Руками (якщо Actions лежить або треба терміново):

```bash
ssh ubuntu@oracle
cd ~/tg-bot-sho-poisty
./scripts/deploy.sh
docker compose logs -f bot        # має бути «Бот запущено (long polling)»; вихід — Ctrl+C
```

**`--build` обов'язковий** (скрипт робить його сам). Без нього `up -d` бере вже
зібраний образ, і бот мовчки працюватиме на старому коді — саме так виникає
крешлуп після `git pull`.

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
- **Деплой в Actions упав з «незакомічені зміни»** → на сервері хтось правив
  файли під git. Зайти, подивитись `git status`, закомітити чи відкотити —
  і перезапустити workflow (Re-run jobs).
- **Кода немає в логах взагалі** → лог обривається одразу після міграцій?
  Такого більше не має бути, але саме так виглядав баг, коли alembic збивав
  root-логер на WARN.

## Моніторинг (ntfy)

Сповіщення про падіння/зупинку/підняття контейнера приходять у додаток ntfy
(топік — в `/etc/ntfy-bot-watch.env` на сервері, в git його немає).
Працює це так: systemd-сервіс `ntfy-bot-watch` на хості слухає `docker events`
через [scripts/ntfy-docker-watch.sh](scripts/ntfy-docker-watch.sh) і шле POST
на ntfy.sh. Сервіс живе поза Docker, тому переживає і ребут, і `compose down`.

```bash
systemctl status ntfy-bot-watch            # чи живий вотчер
journalctl -u ntfy-bot-watch -n 20         # його логи
sudo systemctl restart ntfy-bot-watch      # перезапуск (напр., після зміни топіка)
```

Що надсилається: 🔴 «БОТ ВПАВ» (ненульовий exit code, пріоритет urgent),
🟡 «Бот зупинено» (штатна зупинка/редеплой), 🟢 «Бот піднявся», 🔴 OOM.
Під час редеплою пара «зупинено → піднявся» — це нормально.

## Про сервер

На цій же машині крутяться чужі контейнери — `tg-news-filter` і `my-tg-bot`.
Не чіпати: `docker system prune -a` та подібне знесе і їх.

**Після перезавантаження сервера бот піднімається сам**: у compose стоїть
`restart: unless-stopped`, а служба docker увімкнена на старті. Перевірити:

```bash
docker compose ps                 # бот має бути Up
docker inspect -f '{{.HostConfig.RestartPolicy.Name}}' tg-bot-sho-poisty-bot-1
```

Нюанс: після `docker compose down` контейнера немає і підніматись нічому —
поверне його лише `docker compose up -d`.
