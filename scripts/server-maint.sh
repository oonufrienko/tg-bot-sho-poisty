#!/usr/bin/env bash
# Обслуговування хоста, кличуть systemd-таймери (RUNBOOK.md):
#   server-maint.sh disk   — аларм у ntfy, якщо диск заповнений понад поріг
#   server-maint.sh prune  — прибрати dangling-образи, що лишає кожен --build
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
THRESHOLD="${THRESHOLD:-85}"   # відсотків

case "${1:-}" in
    disk)
        use=$(df --output=pcent / | tail -1 | tr -dc '0-9')
        if [ "$use" -ge "$THRESHOLD" ]; then
            "$DIR/ntfy-send.sh" "Диск заповнено на ${use}%" 5 "floppy_disk" \
                "Кореневий розділ понад поріг ${THRESHOLD}%. Найчастіша причина — старі docker-образи: docker image prune -f (БЕЗ -a: на сервері чужі боти). Ще: du -sh ~/tg-bot-sho-poisty/data"
        fi
        ;;
    prune)
        # Тільки dangling-образи: -a знесло б образи сусідніх ботів.
        docker image prune -f
        ;;
    *)
        echo "Використання: $0 disk|prune" >&2
        exit 64
        ;;
esac
