#!/usr/bin/env bash
# Деплой на сервері: викликається з GitHub Actions по SSH, можна і руками.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ "$(git branch --show-current)" != "main" ]; then
    echo "ПОМИЛКА: на сервері активна не main, а «$(git branch --show-current)» — деплой зупинено." >&2
    exit 1
fi

if ! git diff --quiet HEAD; then
    echo "ПОМИЛКА: на сервері є незакомічені зміни — деплой зупинено." >&2
    git status --short >&2
    exit 1
fi

git fetch origin main
git merge --ff-only origin/main

# --build обов'язковий: без нього up -d підніме старий образ (див. NEXT_STEPS.md).
docker compose up -d --build
docker compose ps
