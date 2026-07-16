#!/usr/bin/env bash
# Якщо контейнер працює, а heartbeat бота застарів (бот завис) — сам рестартує
# контейнер і сповіщає в ntfy. Людина потрібна лише коли прийшла ескалація.
# Запускається systemd-таймером ntfy-heartbeat-check кожні 3 хв (RUNBOOK.md).
# Heartbeat пише сам бот: heartbeat_loop у bot/main.py, файл data/heartbeat.
#
# Стани в $STATE (1 подія ntfy на перехід, без спаму):
#   ok              — heartbeat свіжий
#   stale           — завис, авторестарт виконано, чекаємо на оживання
#   stale-escalated — рестарт не допоміг або був у кулдауні; далі мовчимо
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
CONTAINER="${CONTAINER:-tg-bot-sho-poisty-bot-1}"
HEARTBEAT="${HEARTBEAT:-$DIR/../data/heartbeat}"
MAX_AGE="${MAX_AGE:-300}"                 # секунд без оновлення = «завис»
RESTART_COOLDOWN="${RESTART_COOLDOWN:-1800}"  # не частіше 1 авторестарту на 30 хв
RESTART_GRACE="${RESTART_GRACE:-300}"     # скільки чекати після рестарту, перш ніж ескалювати
STATE="${STATE:-/var/tmp/ntfy-heartbeat.state}"
# Час останнього авторестарту тримаємо окремо від STATE: він має переживати
# «відвис» (скидання епізоду), інакше кулдаун не захистить від петлі
# завис → рестарт → хвилину живий → знову завис.
LAST_RESTART="${LAST_RESTART:-/var/tmp/ntfy-heartbeat.last-restart}"

# Контейнер лежить — про це вже сповістив ntfy-bot-watch, не дублюємо.
running=$(docker inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null || echo false)
[ "$running" = "true" ] || exit 0

now=$(date +%s)
mtime=$(stat -c %Y "$HEARTBEAT" 2>/dev/null || echo 0)
age=$(( now - mtime ))
prev=$(cat "$STATE" 2>/dev/null || echo ok)

if [ "$age" -le "$MAX_AGE" ]; then
    if [ "$prev" != "ok" ]; then
        "$DIR/ntfy-send.sh" "Бот відвис" 3 "green_circle" \
            "Heartbeat знову оновлюється."
        echo ok > "$STATE"
    fi
    exit 0
fi

case "$prev" in
    ok)
        last=$(cat "$LAST_RESTART" 2>/dev/null || echo 0)
        if [ $(( now - last )) -gt "$RESTART_COOLDOWN" ]; then
            docker restart "$CONTAINER" >/dev/null
            echo "$now" > "$LAST_RESTART"
            echo stale > "$STATE"
            "$DIR/ntfy-send.sh" "БОТ ЗАВИС — рестартую" 5 "rotating_light" \
                "Heartbeat не оновлювався ${age}с (поріг ${MAX_AGE}с). Контейнер перезапущено автоматично; якщо не допоможе — прийде ескалація."
        else
            echo stale-escalated > "$STATE"
            "$DIR/ntfy-send.sh" "БОТ ЗАВИС — потрібні руки" 5 "rotating_light" \
                "Heartbeat не оновлювався ${age}с, а авторестарт у кулдауні (був $(( now - last ))с тому, ліміт ${RESTART_COOLDOWN}с). Бот зависає повторно — подивіться: docker compose logs bot"
        fi
        ;;
    stale)
        # Рестарт уже був. Даємо боту RESTART_GRACE на запуск (міграції,
        # webhook, перший heartbeat) — ескалюємо лише коли час вийшов.
        last=$(cat "$LAST_RESTART" 2>/dev/null || echo 0)
        if [ $(( now - last )) -lt "$RESTART_GRACE" ]; then
            exit 0
        fi
        echo stale-escalated > "$STATE"
        "$DIR/ntfy-send.sh" "Рестарт не допоміг — потрібні руки" 5 "sos" \
            "Через $(( now - last ))с після авторестарту heartbeat досі не оновлюється. Подивіться: docker compose logs bot"
        ;;
    *)
        # stale-escalated: людину вже покликали, мовчимо до кінця епізоду.
        ;;
esac
