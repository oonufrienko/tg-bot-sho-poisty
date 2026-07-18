# Graph Report - .  (2026-07-18)

## Corpus Check
- 9 files · ~20,367 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 605 nodes · 1230 edges · 71 communities (37 shown, 34 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 50 edges (avg confidence: 0.66)
- Token cost: 47,292 input · 0 output

## Community Hubs (Navigation)
- LLM Contract & Schemas
- Architecture Rules & Guidelines
- Dish Query Handlers
- Repository SQL Layer
- Group Management Handlers
- ORM Models & Repo Tests
- Recipe Adding Handlers
- Config, Session & Migrations
- LLM Errors & Retry
- Architecture Test Internals
- OpenRouter Client
- Menu Planning Handlers
- Shopping List Aggregation
- Deployment & Secrets
- Recipe Rendering
- Telegram Input Ingestion
- Initial Schema Migration
- Aiogram Bot Symbol
- Package Init
- Recipe Model Reference
- Package Init
- LLMClient Reference
- QueryIntent Reference
- LLMClient Reference
- QueryIntent Reference
- Package Init
- Keyboard Markup Reference
- Package Init
- DishCB Callback Reference
- Exception Reference
- Group Model Reference
- RecentCB Callback Reference
- Generic TypeVar
- Package Init
- Community 37
- Community 38
- Community 39
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Community 47
- Community 48
- Community 49
- Community 50
- Community 51
- Community 52
- Community 53
- Community 54
- Community 56
- Community 58
- Community 60
- Community 62
- Community 63
- Community 64
- Community 65
- Community 66
- Community 67
- Community 68
- Community 69

## God Nodes (most connected - your core abstractions)
1. `LLMClient` - 22 edges
2. `README.md — Що поїсти? bot overview` - 20 edges
3. `Recipe` - 17 edges
4. `QueryIntent` - 17 edges
5. `_make_user_with_recipe()` - 16 edges
6. `render_recipe_list()` - 13 edges
7. `GeminiClient` - 12 edges
8. `run_with_retries()` - 12 edges
9. `run_find_dish()` - 12 edges
10. `LLMQuotaError` - 12 edges

## Surprising Connections (you probably didn't know these)
- `INSTALL.md — server installation guide (bot, watchers, autodeploy)` --references--> `heartbeat_loop()`  [EXTRACTED]
  INSTALL.md → bot/main.py
- `heartbeat_loop()` --shares_data_with--> `scripts/check-heartbeat.sh — heartbeat freshness check + auto-restart`  [EXTRACTED]
  bot/main.py → INSTALL.md
- `_Msg` --uses--> `Settings`  [INFERRED]
  tests/test_admin_stats.py → bot/config.py
- `_Query` --uses--> `Settings`  [INFERRED]
  tests/test_admin_stats.py → bot/config.py
- `test_parse_qty_variants()` --calls--> `parse_qty()`  [EXTRACTED]
  tests/test_shopping_list.py → bot/services/shopping_list.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Hang-detection chain: heartbeat file, host-side checker with auto-restart, and escalation policy form the watchdog** — runbook_heartbeat_autorestart, runbook_heartbeat_escalation, runbook_heartbeat_state_files [EXTRACTED 1.00]
- **Host-side monitoring stack: docker-events watcher, heartbeat watchdog, and disk/prune timers participate in server monitoring** — runbook_ntfy_monitoring, runbook_heartbeat_autorestart, runbook_disk_maintenance [EXTRACTED 1.00]
- **Host-side systemd watcher suite living outside Docker** — install_ntfy_bot_watch_service, install_ntfy_heartbeat_check_timer, install_ntfy_disk_check_timer, install_docker_image_prune_timer, install_ntfy_bot_watch_env [EXTRACTED 1.00]
- **Autodeploy pipeline: merge to main → GitHub Actions → SSH → deploy.sh** — github_workflows_deploy, scripts_deploy_sh, install_autodeploy_setup [EXTRACTED 1.00]
- **Automated Deploy Pipeline (push main -> test -> SSH deploy -> compose rebuild)** — _github_workflows_deploy_test_job, _github_workflows_deploy_deploy_job, docker_compose_bot_service, runbook_operations_runbook [EXTRACTED 1.00]
- **Layer Boundary Rules Enforced Across Config, Docs And Tests** — coderabbit_models_data_only_rule, coderabbit_repo_sole_query_site_rule, coderabbit_thin_handlers_rule, coderabbit_services_tenancy_explicit_rule, claude_layer_rules_enforced_by_tests [INFERRED 0.85]
- **Group Tenancy Isolation Concerns** — readme_group_shared_recipe_base, report_2026_07_14_09_01_cross_group_serve_history, report_2026_07_14_09_01_fsm_group_binding, report_2026_07_14_09_01_group_scoping_invariant, coderabbit_services_tenancy_explicit_rule [INFERRED 0.85]
- **Layered Architecture Rule Set** — architecture_layer_rules, architecture_models_data_only, architecture_repo_single_sql_point, architecture_services_no_telegram, architecture_thin_handlers, architecture_new_feature_new_service [EXTRACTED 1.00]

## Communities (71 total, 34 thin omitted)

### Community 0 - "LLM Contract & Schemas"
Cohesion: 0.10
Nodes (61): Bot, amend_start(), cancel(), create_group_start(), another_dish(), apply_edit(), ask_delete_number(), ask_edit_number() (+53 more)

### Community 1 - "Architecture Rules & Guidelines"
Cohesion: 0.13
Nodes (26): ABC, BaseModel, Recipe, ExtractedIngredient, LLMClient, MenuPlanResult, MenuSlot, QueryIntent (+18 more)

### Community 2 - "Dish Query Handlers"
Cohesion: 0.11
Nodes (36): add_recipe(), clear_served(), count_users(), create_group(), delete_recipe(), ensure_user(), find_recipe_by_title(), get_group() (+28 more)

### Community 3 - "Repository SQL Layer"
Cohesion: 0.10
Nodes (23): heartbeat_loop(), main(), Пише unix-час у файл; якщо event loop завис — файл стає застарілим.      Свіжіст, run_migrations(), docker-compose bot Service, json-file Log Rotation Limits, stop_grace_period 30s for aiogram Shutdown, Restore bot.db BEFORE first docker compose up (+15 more)

### Community 4 - "Group Management Handlers"
Cohesion: 0.17
Nodes (22): AsyncSession, User, add_hint(), AddStates, amend_apply(), handle_media(), Спільний вхід: екстракція + картка підтвердження., save_recipe() (+14 more)

### Community 5 - "ORM Models & Repo Tests"
Cohesion: 0.16
Nodes (22): LLMError, LLMQuotaError, Перевищено ліміт запитів провайдера (HTTP 429)., Exception, T, Спільні ретраї для LLM-провайдерів з класифікацією за HTTP-статусом., Пауза перед наступною спробою; None = помилка постійна, не ретраїмо., retry_delay() (+14 more)

### Community 6 - "Recipe Adding Handlers"
Cohesion: 0.14
Nodes (14): _file_part(), OpenRouterClient, LLM-клієнт через OpenRouter (OpenAI-сумісний API).  Використовується, коли задан, _text_part(), MenuPlanResult, RecipeExtraction, SelectionResult, T (+6 more)

### Community 7 - "Config, Session & Migrations"
Cohesion: 0.11
Nodes (15): _extraction(), _LLM, _Msg, _NoopTyping, Message, _Query, Звʼязка «редагування → картка → Зберегти».  Ці інваріанти живуть у передачі edit, Саме тут ховався баг: картка губила edit_id і «Зберегти» робило копію. (+7 more)

### Community 8 - "LLM Errors & Retry"
Cohesion: 0.14
Nodes (21): _make_user_with_recipe(), Правка міняє текст рецепта, а не його походження чи історію подач., Сценарій бага: створив нову групу → переніс рецепти → запрошений їх бачить., Дублікат за назвою (інший регістр/пробіли) лишається у старій групі., recipe_id з callback-data не має відкривати рецепти чужої групи., ServeHistory має FK на recipes.id без cascade — історію треба прибрати явно., test_category_filter(), test_clear_served_wipes_history_for_group_only() (+13 more)

### Community 9 - "Architecture Test Internals"
Cohesion: 0.11
Nodes (23): Definition of Done, Goal-Driven Execution, Knowledge Graph Freshness Rule, Layer Rules (ARCHITECTURE.md), Simplicity First, Surgical Changes, tg-bot-sho-poisty (project), CodeRabbit Review Configuration (+15 more)

### Community 10 - "OpenRouter Client"
Cohesion: 0.14
Nodes (22): README.md — Що поїсти? bot overview, Auto-deploy: push to main runs tests and deploys via GitHub Actions over SSH executing scripts/deploy.sh, Categories: breakfast, lunch, dinner, dessert, salad, general (+ difficulty 1-4), DB reset procedure: down, backup bot.db, rm, up --build (migrations recreate empty DB), Dish selection queries (what's for dinner, from chicken, etc.), Docker run on server: docker compose up -d --build, Gemini API (free fallback, GEMINI_API_KEY, ~10 req/min free tier), Recommended workflow: create group and make it active before uploading recipes; bot offers transfer otherwise (+14 more)

### Community 11 - "Menu Planning Handlers"
Cohesion: 0.16
Nodes (20): ADMIN_USER_IDS — admins see a '📊 Статистика' button in the group menu (total users, remaining OpenRouter credits); admin status does not grant access — admins must also be in ALLOWED_USER_IDS, ALLOWED_USER_IDS — comma-separated Telegram ids; empty denies everyone (safe default), '*' opens the bot to all of Telegram, Auto-deploy: PR merge to main runs tests and GitHub Actions SSHes in to run scripts/deploy.sh (git pull + rebuild), live in 2-3 min, Daily commands: compose logs, compose down, and DB backup via cp data/bot.db ~/backup-recipes-<date>.db, scripts/deploy.sh — git pull + docker compose rebuild; --build is mandatory (rationale: without --build, up -d reuses the old image and the bot silently runs stale code, causing crashloops after git pull), Disk maintenance: weekly docker-image-prune timer runs `docker image prune -f` (dangling only; -a forbidden — would destroy neighbor bots' images); ntfy-disk-check timer alerts 🔴 every 6h if disk >85% via scripts/server-maint.sh; container logs capped in compose (max-size 10m × 3 files), .env keys: BOT_TOKEN, OPENROUTER_API_KEY (primary LLM), GEMINI_API_KEY (fallback, only if OpenRouter unset), OPENROUTER_MODEL (google/gemini-3.1-flash-lite-preview), ALLOWED_USER_IDS, ADMIN_USER_IDS; at least one LLM key required or the bot won't start, Changing .env requires `docker compose up -d`, never `restart` (rationale: env_file vars are baked into the container at creation; restart reuses the same container with old values, up -d recreates it) (+12 more)

### Community 12 - "Shopping List Aggregation"
Cohesion: 0.20
Nodes (16): Base, Group, GroupMember, RecipeCategory, RecipeMedia, ServeHistory, utcnow(), Останні рекомендовані за датами (свіжа зверху): (ServeHistory, Recipe). (+8 more)

### Community 13 - "Deployment & Secrets"
Cohesion: 0.26
Nodes (18): create_group_finish(), group_menu(), _group_overview(), GroupStates, invite_link(), members_list(), move_recipes_confirm(), move_recipes_skip() (+10 more)

### Community 14 - "Recipe Rendering"
Cohesion: 0.22
Nodes (17): menu_hint(), _plan_for_active_group(), AsyncSession, CallbackQuery, FSMContext, Message, User, run_menu_flow() (+9 more)

### Community 15 - "Telegram Input Ingestion"
Cohesion: 0.18
Nodes (16): fetch_remaining_credits(), AsyncClient, Залишок кредитів на OpenRouter — для адмінської статистики.  Окремо від LLMClien, Скільки доларів лишилось. None — якщо дізнатись не вдалося.      Одна спроба без, _request(), credits_client(), make_settings(), AsyncClient (+8 more)

### Community 16 - "Initial Schema Migration"
Cohesion: 0.16
Nodes (11): Any, async_sessionmaker, BaseMiddleware, get_settings(), get_session_factory(), AsyncSession, AccessDbMiddleware, Whitelist + сесія БД + реєстрація користувача для кожного апдейта. (+3 more)

### Community 17 - "Aiogram Bot Symbol"
Cohesion: 0.21
Nodes (17): AsyncFunctionDef, FunctionDef, Module, _imported_modules(), _imported_names_from(), _is_property(), _is_trivial_property(), _parse() (+9 more)

### Community 18 - "Package Init"
Cohesion: 0.25
Nodes (12): aggregate(), _format_amount(), parse_qty(), Агрегація інгредієнтів у список покупок., «1,5» → 1.5; «1/2» → 0.5; «2-3» → 3 (беремо більше, щоб точно вистачило)., Сумує кількості за (назва, одиниця). Повертає готові рядки списку покупок., test_aggregate_decimal_comma_output(), test_aggregate_keeps_different_units_separate() (+4 more)

### Community 19 - "Recipe Model Reference"
Cohesion: 0.31
Nodes (12): _by_category(), Групує за першою категорією рецепта, секції у порядку CATEGORIES., Список за категоріями. Повертає (текст, id у порядку нумерації)., render_recipe_list(), make(), render_recipe_list: групування за категоріями та наскрізна нумерація., test_difficulty_rendered_as_stars(), test_multi_category_recipe_shown_once_under_first_category() (+4 more)

### Community 20 - "Package Init"
Cohesion: 0.22
Nodes (7): show_stats(), _Msg, Message, _Query, Кнопки не-адмін не бачить, але callback_data підробна — гвард на сервері., test_admin_sees_user_count_and_credits(), test_non_admin_gets_alert_even_with_forged_callback()

### Community 21 - "LLMClient Reference"
Cohesion: 0.31
Nodes (9): help_command(), AsyncSession, Message, User, start(), start_with_link(), main_keyboard(), CommandObject (+1 more)

### Community 22 - "QueryIntent Reference"
Cohesion: 0.28
Nodes (9): services/ingestion.py adapter (sanctioned aiogram exception), Layer Rules (handlers → services → repo → models), Rule 1: Models are data-only, Rule 6: New feature = new service, Rule 2: repo.py is the single SQL point, Rule 3: Services know nothing about Telegram, Architecture Test Suite (tests/test_architecture.py), Rule 4: Thin handlers (no SQL, no business rules, no prompts) (+1 more)

### Community 23 - "LLMClient Reference"
Cohesion: 0.22
Nodes (4): BaseSettings, Відкритий доступ — лише за явним ALLOWED_USER_IDS=* (dev-режим)., Адміни бачать «Статистика». Без '*'-магії: порожнє = адмінів немає., Settings

### Community 24 - "QueryIntent Reference"
Cohesion: 0.36
Nodes (7): collect_input(), _download(), Bot, Message, Перетворення повідомлення Telegram на вхід для екстракції рецепта., Витягує текст і файли з повідомлення (фото/скрін/PDF/текст/форвард)., RecipeInput

### Community 25 - "Package Init"
Cohesion: 0.67
Nodes (4): Deploy Concurrency Gate, SSH Deploy Job, Test & Deploy GitHub Actions Workflow, CI Test Job (uv sync + pytest)

### Community 26 - "Keyboard Markup Reference"
Cohesion: 0.50
Nodes (4): .github/workflows/deploy.yml — Test & Deploy workflow (push to main + workflow_dispatch), GitHub Actions autodeploy setup (deploy key + 4 secrets + workflow_dispatch smoke test), systemd reads watcher scripts straight from the git working tree, so git merge auto-updates them (unit files excepted — need re-copy + daemon-reload), scripts/deploy.sh — git ff-merge + compose up -d --build

### Community 27 - "Package Init"
Cohesion: 0.83
Nodes (3): notify(), ntfy-docker-watch.sh script, wait_ready()

## Knowledge Gaps
- **18 isolated node(s):** `tg-bot-sho-poisty (project)`, `deploy.sh script`, `ntfy-send.sh script`, `server-maint.sh script`, `check-heartbeat.sh script` (+13 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **34 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `New-server-from-scratch checklist (8 ordered steps)` connect `Repository SQL Layer` to `Menu Planning Handlers`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `LLMClient` (e.g. with `AddStates` and `GeminiClient`) actually correct?**
  _`LLMClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `tg-bot-sho-poisty (project)`, `deploy.sh script`, `ntfy-send.sh script` to the rest of the system?**
  _18 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `LLM Contract & Schemas` be split into smaller, more focused modules?**
  _Cohesion score 0.09711538461538462 - nodes in this community are weakly interconnected._
- **Should `Architecture Rules & Guidelines` be split into smaller, more focused modules?**
  _Cohesion score 0.12560975609756098 - nodes in this community are weakly interconnected._
- **Should `Dish Query Handlers` be split into smaller, more focused modules?**
  _Cohesion score 0.11411411411411411 - nodes in this community are weakly interconnected._
- **Should `Repository SQL Layer` be split into smaller, more focused modules?**
  _Cohesion score 0.10461538461538461 - nodes in this community are weakly interconnected._