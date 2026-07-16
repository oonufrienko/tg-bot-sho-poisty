# Встановлення моніторингу (вотчерів) на сервері

Одноразова інструкція: як з нуля підняти всі сповіщення в ntfy для бота.
Щоденні команди й «що робити, коли прийшов аларм» — у [RUNBOOK.md](RUNBOOK.md).

## Що буде встановлено

| Юніт | Що робить | Як часто |
|---|---|---|
| `ntfy-bot-watch.service` | слухає `docker events`: 🔴 падіння/OOM, 🟡 зупинка, 🟢 «піднявся» (чекає готовності за heartbeat) | постійно |
| `ntfy-heartbeat-check.timer` | 🔴 «БОТ ЗАВИС», якщо контейнер Up, а heartbeat застарів | кожні 3 хв |
| `ntfy-disk-check.timer` | 🔴 диск заповнений понад 85% | кожні 6 год |
| `docker-image-prune.timer` | прибирає dangling-образи від `--build` (тільки їх!) | щотижня |

Усі скрипти лежать у [scripts/](scripts/), юніти — у [scripts/systemd/](scripts/systemd/).
Вотчери живуть на хості поза Docker, тому переживають і ребут, і `compose down`.

## Передумови

- `curl` і `jq` (`sudo apt install -y curl jq`);
- користувач у групі `docker` (`id` має показувати `docker`);
- репозиторій за шляхом `/home/ubuntu/tg-bot-sho-poisty` — якщо інший,
  поправте `ExecStart` в юніт-файлах перед копіюванням.

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
пара 🟡 «Бот зупинено» → 🟢 «Бот піднявся».

## Як це влаштовано (якщо треба лагодити)

- Сповіщення шле [scripts/ntfy-send.sh](scripts/ntfy-send.sh) — JSON POST на
  `https://ntfy.sh` (сервер можна замінити змінною `NTFY_SERVER` у env-файлі).
- Heartbeat пише сам бот: `heartbeat_loop` у [bot/main.py](bot/main.py)
  щохвилини оновлює `data/heartbeat`; свіжість перевіряє
  [scripts/check-heartbeat.sh](scripts/check-heartbeat.sh). Анти-спам стан —
  `/var/tmp/ntfy-heartbeat.state`.
- Пороги міняються без правки коду: env-змінні `MAX_AGE` (heartbeat, сек)
  і `THRESHOLD` (диск, %) можна дописати у `/etc/ntfy-bot-watch.env`,
  після чого `sudo systemctl restart ntfy-bot-watch` (таймери підхоплять самі).
- Логи будь-якого юніта: `journalctl -u <назва> -n 20`.
