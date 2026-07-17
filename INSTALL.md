# Встановлення на сервері: бот, вотчери, автодеплой

Одноразова інструкція для нового сервера (або переносу на інший інстанс).
Щоденні команди й «що робити, коли прийшов аларм» — у [RUNBOOK.md](RUNBOOK.md).

## Новий сервер з нуля — порядок дій

Кожен крок розписаний нижче або за посиланням; тут — правильна послідовність.

1. **Docker + compose**, служба увімкнена: `sudo systemctl enable --now docker`
   (без цього після ребуту не спрацює `restart: unless-stopped`).
   Користувача — у групу `docker`.
2. **Клонувати репо саме в `~/tg-bot-sho-poisty`.** Назва каталогу — не
   косметика: compose успадковує від неї імʼя проєкту, тому контейнер
   зветься `tg-bot-sho-poisty-bot-1`, і саме цю назву очікують усі вотчери.
   Інший каталог → інша назва контейнера → вотчери **мовчки** стежать за
   неіснуючим контейнером: ні помилок, ні алертів. Якщо назву змінити все ж
   треба — допишіть `CONTAINER=<нова-назва>` у `/etc/ntfy-bot-watch.env`.
3. **`.env`**: `cp .env.example .env` і заповнити (ключі описані в
   [README.md](README.md) та [RUNBOOK.md](RUNBOOK.md)).
4. **Відновити базу — ДО першого запуску.** Скопіювати `bot.db` зі старого
   сервера (або з бекапа) у `data/`:
   `scp ubuntu@СТАРИЙ:~/tg-bot-sho-poisty/data/bot.db data/`
   Якщо цього не зробити, перший `up -d` створить порожню базу, і бот
   стартуватиме без жодного рецепта. Для свідомого старту з нуля крок
   пропустити.
5. **Запустити**: `docker compose up -d --build`, у логах має бути
   «Бот запущено (long polling)».
6. **Вотчери** — кроки 1–3 нижче.
7. **Автодеплой** — розділ «Автодеплой (GitHub Actions)» нижче.
8. Наприкінці — **fire drill** із RUNBOOK.md: переконатись, що авторестарт
   реально спрацьовує на цьому інстансі.

## Що буде встановлено

| Юніт | Що робить | Як часто |
|---|---|---|
| `ntfy-bot-watch.service` | слухає `docker events`: 🔴 падіння/OOM, 🟡 зупинка, 🟢 «піднявся» (чекає готовності за heartbeat) | постійно |
| `ntfy-heartbeat-check.timer` | контейнер Up, а heartbeat застарів → **сам рестартує** + 🔴 «БОТ ЗАВИС — рестартую» | кожні 3 хв |
| `ntfy-disk-check.timer` | 🔴 диск заповнений понад 85% | кожні 6 год |
| `docker-image-prune.timer` | прибирає dangling-образи від `--build` (тільки їх!) | щотижня |

Усі скрипти лежать у [scripts/](scripts/), юніти — у [scripts/systemd/](scripts/systemd/).
Вотчери живуть на хості поза Docker, тому переживають і ребут, і `compose down`.

## Передумови

- `curl` і `jq` (`sudo apt install -y curl jq`);
- користувач у групі `docker` (`id` має показувати `docker`);
- репозиторій за шляхом `/home/ubuntu/tg-bot-sho-poisty` — якщо інший, то
  **два** наслідки: поправити `ExecStart` в юніт-файлах перед копіюванням
  І задати `CONTAINER=` у `/etc/ntfy-bot-watch.env` (назва контейнера походить
  від назви каталогу — див. крок 2 чеклиста вище).

## Крок 1: топік ntfy

Топік — це і адреса, і «пароль»: хто знає назву, той читає. Тому назва
має бути невгадуваною, і в git їй не місце.

```bash
echo "NTFY_TOPIC=sho-poisty-alerts-$(openssl rand -hex 4)" | sudo tee /etc/ntfy-bot-watch.env
sudo chmod 600 /etc/ntfy-bot-watch.env
```

У додатку ntfy на телефоні: **+ → Subscribe to topic** → назва з файлу вище.

## Крок 2: юніти

```bash
cd ~/tg-bot-sho-poisty
sudo cp scripts/systemd/* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now ntfy-bot-watch.service \
    ntfy-heartbeat-check.timer ntfy-disk-check.timer docker-image-prune.timer
```

## Крок 3: перевірка

```bash
systemctl is-active ntfy-bot-watch                      # active
systemctl list-timers 'ntfy-*' 'docker-image-prune*'    # 3 таймери
# тестове сповіщення (має прийти на телефон):
sudo sh -c '. /etc/ntfy-bot-watch.env && export NTFY_TOPIC && /home/ubuntu/tg-bot-sho-poisty/scripts/ntfy-send.sh "Тест" 3 wave "Вотчери встановлено"'
```

Бойова перевірка — будь-який редеплой (мерж у main): у ntfy має прийти
пара 🟡 «Бот зупинено» → 🟢 «Бот піднявся». Повний тест ланцюга зависання
(з навмисним заморожуванням бота) — «fire drill» у [RUNBOOK.md](RUNBOOK.md).

## Автодеплой (GitHub Actions)

Мерж у `main` запускає [.github/workflows/deploy.yml](.github/workflows/deploy.yml):
тести → SSH на сервер → `scripts/deploy.sh` (git ff-merge + `compose up -d
--build`). Побічний бонус: git-merge оновлює і хост-скрипти вотчерів — systemd
читає їх прямо з робочого дерева, тож зміни в `scripts/*.sh` доїжджають без
жодних додаткових кроків (юніт-файли — виняток: після їх зміни треба повторити
крок 2 і `daemon-reload`).

При переносі на новий сервер треба перевʼязати SSH. На своїй машині:

```bash
ssh-keygen -t ed25519 -f deploy_key -N ""   # окремий ключ ТІЛЬКИ для деплою
ssh-copy-id -i deploy_key.pub ubuntu@НОВИЙ_ХОСТ   # або вручну в ~/.ssh/authorized_keys
ssh-keyscan -H НОВИЙ_ХОСТ                   # вивід піде в SSH_KNOWN_HOSTS
```

У репо: Settings → Secrets and variables → Actions — оновити чотири секрети:

| Секрет | Значення |
|---|---|
| `SSH_PRIVATE_KEY` | вміст файлу `deploy_key` (приватний, з BEGIN/END) |
| `SSH_USER` | `ubuntu` |
| `SSH_HOST` | адреса нового сервера |
| `SSH_KNOWN_HOSTS` | вивід `ssh-keyscan -H <хост>` |

Локальний `deploy_key` після цього видалити — він живе лише в секретах.
Перший запуск — руками, до будь-якого мержу: вкладка Actions → «Test & Deploy»
→ Run workflow (`workflow_dispatch` у воркфлові існує саме для такої перевірки
SSH-звʼязки). Якщо деплой упав з «незакомічені зміни» — на сервері правили
файли під git; розібратись через `git status` там.

## Як це влаштовано (якщо треба лагодити)

- Сповіщення шле [scripts/ntfy-send.sh](scripts/ntfy-send.sh) — JSON POST на
  `https://ntfy.sh` (сервер можна замінити змінною `NTFY_SERVER` у env-файлі).
- Heartbeat пише сам бот: `heartbeat_loop` у [bot/main.py](bot/main.py)
  щохвилини оновлює `data/heartbeat`; свіжість перевіряє
  [scripts/check-heartbeat.sh](scripts/check-heartbeat.sh). Анти-спам стан —
  `/var/tmp/ntfy-heartbeat.state`.
- Пороги міняються без правки коду: env-змінні `MAX_AGE` (heartbeat, сек),
  `RESTART_COOLDOWN` (мінімальна пауза між авторестартами при зависанні, сек,
  типово 1800), `RESTART_GRACE` (скільки чекати оживання heartbeat після
  авторестарту, перш ніж ескалювати, сек, типово 300) і `THRESHOLD` (диск, %)
  можна дописати у
  `/etc/ntfy-bot-watch.env`, після чого `sudo systemctl restart ntfy-bot-watch`
  (таймери підхоплять самі). Мітка останнього авторестарту —
  `/var/tmp/ntfy-heartbeat.last-restart`.
- Логи будь-якого юніта: `journalctl -u <назва> -n 20`.
