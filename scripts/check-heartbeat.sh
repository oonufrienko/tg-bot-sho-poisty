#!/usr/bin/env bash
# Аларм у ntfy, якщо контейнер працює, а heartbeat бота застарів (бот завис).
# Запускається systemd-таймером ntfy-heartbeat-check кожні 3 хв (RUNBOOK.md).
# Heartbeat пише сам бот: heartbeat_loop у bot/main.py, файл data/heartbeat.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
CONTAINER="${CONTAINER:-tg-bot-sho-poisty-bot-1}"
HEARTBEAT="${HEARTBEAT:-$DIR/../data/heartbeat}"
MAX_AGE="${MAX_AGE:-300}"                 # секунд без оновлення = «завис»
STATE="${STATE:-/var/tmp/ntfy-heartbeat.state}"  # анти-спам: 1 аларм на епізод

# Контейнер лежить — про це вже сповістив ntfy-bot-watch, не дублюємо.
running=$(docker inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null || echo false)
[ "$running" = "true" ] || exit 0

mtime=$(stat -c %Y "$HEARTBEAT" 2>/dev/null || echo 0)
age=$(( $(date +%s) - mtime ))
prev=$(cat "$STATE" 2>/dev/null || echo ok)

if [ "$age" -gt "$MAX_AGE" ]; then
    if [ "$prev" != "stale" ]; then
        "$DIR/ntfy-send.sh" "БОТ ЗАВИС" 5 "rotating_light" \
            "Контейнер працює, але heartbeat не оновлювався ${age}с (поріг ${MAX_AGE}с). Спробуй: docker compose restart bot"
        echo stale > "$STATE"
    fi
elif [ "$prev" = "stale" ]; then
    "$DIR/ntfy-send.sh" "Бот відвис" 3 "green_circle" \
        "Heartbeat знову оновлюється."
    echo ok > "$STATE"
fi
