#!/usr/bin/env bash
# Слухає docker events контейнера бота і шле сповіщення в ntfy.
# Запускається systemd-сервісом ntfy-bot-watch на хості (див. RUNBOOK.md);
# топік живе в /etc/ntfy-bot-watch.env, НЕ в репозиторії.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
CONTAINER="${CONTAINER:-tg-bot-sho-poisty-bot-1}"
HEARTBEAT="${HEARTBEAT:-$DIR/../data/heartbeat}"
READY_TIMEOUT="${READY_TIMEOUT:-90}"   # скільки секунд чекати готовності бота

notify() { # $1 title, $2 priority (1-5), $3 tags через кому, $4 message
    "$DIR/ntfy-send.sh" "$@" || echo "ntfy недоступний, подію втрачено: $1" >&2
}

# Подія start означає лише «процес запущено» — бот ще ганяє міграції.
# Готовність = heartbeat, записаний ПІСЛЯ старту контейнера.
wait_ready() {
    local started deadline mtime
    started=$(date -d "$(docker inspect -f '{{.State.StartedAt}}' "$CONTAINER" 2>/dev/null)" +%s 2>/dev/null) \
        || return 1
    deadline=$(( $(date +%s) + READY_TIMEOUT ))
    while [ "$(date +%s)" -lt "$deadline" ]; do
        mtime=$(stat -c %Y "$HEARTBEAT" 2>/dev/null || echo 0)
        [ "$mtime" -ge "$started" ] && return 0
        sleep 5
    done
    return 1
}

docker events \
    --filter "container=$CONTAINER" \
    --filter type=container \
    --filter event=start --filter event=die --filter event=oom \
    --format '{{.Action}} {{index .Actor.Attributes "exitCode"}}' \
| while read -r action exit_code; do
    case "$action" in
        start)
            if wait_ready; then
                notify "Бот піднявся" 3 "green_circle" \
                    "Бот працює: heartbeat свіжіший за старт контейнера."
            else
                notify "Бот не вийшов на роботу" 5 "rotating_light" \
                    "Контейнер $CONTAINER стартував, але heartbeat не з'явився за ${READY_TIMEOUT}с. Дивись: docker compose logs bot | tail -30"
            fi
            ;;
        die)
            # 0 — чистий вихід, 143 — SIGTERM (compose stop/редеплой)
            if [ "${exit_code:-0}" = "0" ] || [ "${exit_code:-}" = "143" ]; then
                notify "Бот зупинено" 3 "yellow_circle" \
                    "Контейнер $CONTAINER зупинився штатно (exit $exit_code). Якщо це редеплой — зараз підніметься."
            else
                notify "БОТ ВПАВ" 5 "rotating_light" \
                    "Контейнер $CONTAINER помер з кодом ${exit_code:-?}. Дивись: docker compose logs bot | tail -30"
            fi
            ;;
        oom)
            notify "OOM: боту не вистачило пам'яті" 5 "rotating_light" \
                "Ядро вбило процес у $CONTAINER через брак пам'яті. Перевір swap (README, секція про 1 ГБ RAM)."
            ;;
    esac
done
