#!/usr/bin/env bash
# Слухає docker events контейнера бота і шле сповіщення в ntfy.
# Запускається systemd-сервісом ntfy-bot-watch на хості (див. NEXT_STEPS.md);
# топік живе в /etc/ntfy-bot-watch.env, НЕ в репозиторії.
set -euo pipefail

: "${NTFY_TOPIC:?NTFY_TOPIC не задано}"
NTFY_SERVER="${NTFY_SERVER:-https://ntfy.sh}"
CONTAINER="${CONTAINER:-tg-bot-sho-poisty-bot-1}"

# JSON-публікація: заголовки HTTP не дружать з кирилицею, тіло — дружить.
notify() { # $1 title, $2 priority (1-5), $3 tags через кому, $4 message
    jq -cn --arg topic "$NTFY_TOPIC" --arg title "$1" --argjson prio "$2" \
        --arg tags "$3" --arg msg "$4" \
        '{topic: $topic, title: $title, priority: $prio,
          tags: ($tags | split(",")), message: $msg}' \
        | curl -fsS --max-time 10 -d @- "$NTFY_SERVER" >/dev/null \
        || echo "ntfy недоступний, подію втрачено: $1" >&2
}

docker events \
    --filter "container=$CONTAINER" \
    --filter type=container \
    --filter event=start --filter event=die --filter event=oom \
    --format '{{.Status}} {{index .Actor.Attributes "exitCode"}}' \
| while read -r status exit_code; do
    case "$status" in
        start)
            notify "Бот піднявся" 3 "green_circle" \
                "Контейнер $CONTAINER запущено."
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
