#!/usr/bin/env bash
# Шле сповіщення в ntfy: ntfy-send.sh TITLE PRIORITY TAGS MESSAGE
# Топік бере з NTFY_TOPIC (на сервері — /etc/ntfy-bot-watch.env).
# JSON-публікація: заголовки HTTP не дружать з кирилицею, тіло — дружить.
set -euo pipefail

: "${NTFY_TOPIC:?NTFY_TOPIC не задано}"
NTFY_SERVER="${NTFY_SERVER:-https://ntfy.sh}"

jq -cn --arg topic "$NTFY_TOPIC" --arg title "$1" --argjson prio "$2" \
    --arg tags "$3" --arg msg "$4" \
    '{topic: $topic, title: $title, priority: $prio,
      tags: ($tags | split(",")), message: $msg}' \
    | curl -fsS --max-time 10 -d @- "$NTFY_SERVER" >/dev/null
