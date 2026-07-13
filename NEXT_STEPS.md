# Що залишилось зробити (≈10 хвилин)

## Вже зроблено ✅

- Проєкт скопійовано на сервер: `ssh ubuntu@oracle`, каталог `~/tg-bot-sho-poisty`
- Docker-образ зібрано, міграції БД перевірено — все працює
- Swap 2 ГБ і Docker на сервері вже були налаштовані
- На сервері створено `.env` із заготовкою — **треба вписати справжні значення**

## Ваші кроки

### 1. Отримайте три значення

| Що | Де взяти |
|---|---|
| `BOT_TOKEN` | Telegram → [@BotFather](https://t.me/BotFather) → `/newbot` → скопіювати токен |
| `GEMINI_API_KEY` | https://aistudio.google.com/apikey → «Create API key» (безкоштовно) |
| `ALLOWED_USER_IDS` | Ваш id: напишіть боту [@userinfobot](https://t.me/userinfobot) |

### 2. Впишіть їх у .env на сервері

```bash
ssh ubuntu@oracle
cd ~/tg-bot-sho-poisty
nano .env          # вписати три значення, зберегти: Ctrl+O, Enter, Ctrl+X
```

`ALLOWED_USER_IDS` — поки що лише ваш id; id дружини/мами додасте потім через кому
(наприклад `123456,789012`) і перезапустите бота (команда нижче).

### 3. Запустіть бота

```bash
docker compose up -d
docker compose logs -f bot    # має з'явитись «Бот запущено (long polling)»; вихід — Ctrl+C
```

### 4. Перевірте в Telegram

1. Відкрийте свого бота → `/start`
2. Надішліть будь-який рецепт текстом або фото → підтвердіть збереження
3. Спитайте «що приготувати?»
4. Кнопка «👨‍👩‍👧 Група» → «➕ Створити групу» → «Сім'я» → перешліть
   invite-посилання рідним (їхні id теж мають бути в `ALLOWED_USER_IDS`!)

## Корисні команди (на сервері, з ~/tg-bot-sho-poisty)

```bash
docker compose logs -f bot        # логи
docker compose restart            # перезапуск (після зміни .env)
docker compose down               # зупинити
cp data/bot.db ~/backup-recipes-$(date +%F).db   # бекап бази рецептів
```

## Оновлення коду (з Mac, після змін у проєкті)

```bash
rsync -az --exclude '.venv' --exclude 'data' --exclude '.env' \
  --exclude '__pycache__' --exclude '.pytest_cache' --exclude '*.egg-info' \
  ./ ubuntu@oracle:~/tg-bot-sho-poisty/
ssh ubuntu@oracle "cd ~/tg-bot-sho-poisty && docker compose up -d --build"
```

## Якщо щось не так

- **Бот не відповідає** → `docker compose logs bot | tail -30`: якщо там
  «Unauthorized» — невірний BOT_TOKEN; якщо помилки Gemini — перевірте ключ.
- **«Це приватний сімейний бот»** → вашого id немає в `ALLOWED_USER_IDS`
  (або забули перезапустити після зміни .env).
- На сервері також працюють `tg-news-filter` і `my-tg-bot` — я їх не чіпав.
