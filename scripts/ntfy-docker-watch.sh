#!/usr/bin/env bash
# Слухає docker events контейнера бота і шле сповіщення в ntfy.
# Запускається systemd-сервісом ntfy-bot-watch на хості (див. NEXT_STEPS.md);
# топік живе в /etc/ntfy-bot-watch.env, НЕ в репозиторії.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
CONTAINER="${CONTAINER:-tg-bot-sho-poisty-bot-1}"

notify() { # $1 title, $2 priority (1-5), $3 tags через кому, $4 message
    "$DIR/ntfy-send.sh" "$@" || echo "ntfy недоступний, подію втрачено: $1" >&2
}

docker events \
    --filter "container=$CONTAINER" \
    --filter type=container \
    --filter event=start --filter event=die --filter event=oom \
    --format '{{.Action}} {{index .Actor.Attributes "exitCode"}}' \
| while read -r action exit_code; do
    case "$action" in
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
