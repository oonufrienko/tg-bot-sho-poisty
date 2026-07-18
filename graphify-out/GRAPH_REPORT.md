# Graph Report - .  (2026-07-18)

## Corpus Check
- 5 files · ~20,448 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 609 nodes · 1223 edges · 66 communities (31 shown, 35 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 48 edges (avg confidence: 0.66)
- Token cost: 0 input · 0 output

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
- Package Init
- Keyboard Markup Reference
- Package Init
- Package Init
- DishCB Callback Reference
- Exception Reference
- Group Model Reference
- Project Root Node
- RecentCB Callback Reference
- Generic TypeVar
- Package Init
- Community 37
- Community 38
- Community 39
- Community 40
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47
- Community 48
- Community 49
- Community 51
- Community 53
- Community 55
- Community 57
- Community 58
- Community 59
- Community 60
- Community 61
- Community 62
- Community 63
- Community 65

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
- `test_parse_qty_variants()` --calls--> `parse_qty()`  [EXTRACTED]
  tests/test_shopping_list.py → bot/services/shopping_list.py
- `test_aggregate_decimal_comma_output()` --calls--> `aggregate()`  [EXTRACTED]
  tests/test_shopping_list.py → bot/services/shopping_list.py
- `test_aggregate_keeps_different_units_separate()` --calls--> `aggregate()`  [EXTRACTED]
  tests/test_shopping_list.py → bot/services/shopping_list.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Ланцюг heartbeat + авторестарт: бот пише heartbeat → check-heartbeat.sh перевіряє й рестартує → стан у файлах на хості** — runbook_heartbeat_loop, runbook_check_heartbeat_sh, runbook_heartbeat_state_files [EXTRACTED 1.00]
- **Моніторинг ntfy: вотчер подій docker + heartbeat-детектор + обслуговування диска** — runbook_ntfy_bot_watch, runbook_check_heartbeat_sh, runbook_server_maint_sh [EXTRACTED 1.00]
- **Host-side systemd watcher suite living outside Docker** — install_ntfy_bot_watch_service, install_ntfy_heartbeat_check_timer, install_ntfy_disk_check_timer, install_docker_image_prune_timer, install_ntfy_bot_watch_env [EXTRACTED 1.00]
- **Autodeploy pipeline: merge to main → GitHub Actions → SSH → deploy.sh** — github_workflows_deploy, scripts_deploy_sh, install_autodeploy_setup [EXTRACTED 1.00]
- **Automated Deploy Pipeline (push main -> test -> SSH deploy -> compose rebuild)** — _github_workflows_deploy_test_job, _github_workflows_deploy_deploy_job, docker_compose_bot_service, runbook_operations_runbook [EXTRACTED 1.00]
- **Layer Boundary Rules Enforced Across Config, Docs And Tests** — coderabbit_models_data_only_rule, coderabbit_repo_sole_query_site_rule, coderabbit_thin_handlers_rule, coderabbit_services_tenancy_explicit_rule, claude_layer_rules_enforced_by_tests [INFERRED 0.85]
- **Group Tenancy Isolation Concerns** — readme_group_shared_recipe_base, report_2026_07_14_09_01_cross_group_serve_history, report_2026_07_14_09_01_fsm_group_binding, report_2026_07_14_09_01_group_scoping_invariant, coderabbit_services_tenancy_explicit_rule [INFERRED 0.85]
- **Layered Architecture Rule Set** — architecture_layer_rules, architecture_models_data_only, architecture_repo_single_sql_point, architecture_services_no_telegram, architecture_thin_handlers, architecture_new_feature_new_service [EXTRACTED 1.00]

## Communities (66 total, 35 thin omitted)

### Community 0 - "LLM Contract & Schemas"
Cohesion: 0.10
Nodes (61): Bot, amend_start(), cancel(), create_group_start(), another_dish(), apply_edit(), ask_delete_number(), ask_edit_number() (+53 more)

### Community 1 - "Architecture Rules & Guidelines"
Cohesion: 0.06
Nodes (54): AsyncClient, create_group_finish(), group_menu(), _group_overview(), GroupStates, invite_link(), members_list(), move_recipes_confirm() (+46 more)

### Community 2 - "Dish Query Handlers"
Cohesion: 0.10
Nodes (38): ABC, BaseModel, menu_hint(), _plan_for_active_group(), AsyncSession, CallbackQuery, FSMContext, Message (+30 more)

### Community 3 - "Repository SQL Layer"
Cohesion: 0.10
Nodes (34): Base, Group, GroupMember, Recipe, RecipeCategory, RecipeMedia, ServeHistory, utcnow() (+26 more)

### Community 4 - "Group Management Handlers"
Cohesion: 0.11
Nodes (36): add_recipe(), clear_served(), count_users(), create_group(), delete_recipe(), ensure_user(), find_recipe_by_title(), get_group() (+28 more)

### Community 5 - "ORM Models & Repo Tests"
Cohesion: 0.10
Nodes (15): Any, async_sessionmaker, BaseMiddleware, BaseSettings, get_settings(), Відкритий доступ — лише за явним ALLOWED_USER_IDS=* (dev-режим)., Адміни бачать «Статистика». Без '*'-магії: порожнє = адмінів немає., Settings (+7 more)

### Community 6 - "Recipe Adding Handlers"
Cohesion: 0.10
Nodes (23): heartbeat_loop(), main(), Пише unix-час у файл; якщо event loop завис — файл стає застарілим.      Свіжіст, run_migrations(), docker-compose bot Service, json-file Log Rotation Limits, stop_grace_period 30s for aiogram Shutdown, Restore bot.db BEFORE first docker compose up (+15 more)

### Community 7 - "Config, Session & Migrations"
Cohesion: 0.16
Nodes (22): LLMError, LLMQuotaError, Перевищено ліміт запитів провайдера (HTTP 429)., Exception, T, Спільні ретраї для LLM-провайдерів з класифікацією за HTTP-статусом., Пауза перед наступною спробою; None = помилка постійна, не ретраїмо., retry_delay() (+14 more)

### Community 8 - "LLM Errors & Retry"
Cohesion: 0.14
Nodes (14): _file_part(), OpenRouterClient, LLM-клієнт через OpenRouter (OpenAI-сумісний API).  Використовується, коли задан, _text_part(), MenuPlanResult, RecipeExtraction, SelectionResult, T (+6 more)

### Community 9 - "Architecture Test Internals"
Cohesion: 0.11
Nodes (15): _extraction(), _LLM, _Msg, _NoopTyping, Message, _Query, Звʼязка «редагування → картка → Зберегти».  Ці інваріанти живуть у передачі edit, Саме тут ховався баг: картка губила edit_id і «Зберегти» робило копію. (+7 more)

### Community 10 - "OpenRouter Client"
Cohesion: 0.14
Nodes (21): _make_user_with_recipe(), Правка міняє текст рецепта, а не його походження чи історію подач., Сценарій бага: створив нову групу → переніс рецепти → запрошений їх бачить., Дублікат за назвою (інший регістр/пробіли) лишається у старій групі., recipe_id з callback-data не має відкривати рецепти чужої групи., ServeHistory має FK на recipes.id без cascade — історію треба прибрати явно., test_category_filter(), test_clear_served_wipes_history_for_group_only() (+13 more)

### Community 11 - "Menu Planning Handlers"
Cohesion: 0.16
Nodes (21): AsyncSession, User, add_hint(), AddStates, amend_apply(), handle_media(), Спільний вхід: екстракція + картка підтвердження., save_recipe() (+13 more)

### Community 12 - "Shopping List Aggregation"
Cohesion: 0.11
Nodes (23): Definition of Done, Goal-Driven Execution, Knowledge Graph Freshness Rule, Layer Rules (ARCHITECTURE.md), Simplicity First, Surgical Changes, tg-bot-sho-poisty (project), CodeRabbit Review Configuration (+15 more)

### Community 13 - "Deployment & Secrets"
Cohesion: 0.14
Nodes (22): README.md — Що поїсти? bot overview, Auto-deploy: push to main runs tests and deploys via GitHub Actions over SSH executing scripts/deploy.sh, Categories: breakfast, lunch, dinner, dessert, salad, general (+ difficulty 1-4), DB reset procedure: down, backup bot.db, rm, up --build (migrations recreate empty DB), Dish selection queries (what's for dinner, from chicken, etc.), Docker run on server: docker compose up -d --build, Gemini API (free fallback, GEMINI_API_KEY, ~10 req/min free tier), Recommended workflow: create group and make it active before uploading recipes; bot offers transfer otherwise (+14 more)

### Community 14 - "Recipe Rendering"
Cohesion: 0.14
Nodes (21): ADMIN_USER_IDS: адміни бачать «📊 Статистика» у головному меню (користувачі, баланс OpenRouter); адмін теж має бути в ALLOWED_USER_IDS, ALLOWED_USER_IDS: id через кому; порожнє — не пускає нікого (безпечно за замовчуванням); * — відкриває бота всім у Telegram, Автодеплой: мерж PR у main → GitHub Actions → SSH → scripts/deploy.sh, scripts/check-heartbeat.sh (таймер ntfy-heartbeat-check, кожні 3 хв): heartbeat старше 5 хв → сам перезапускає контейнер і шле 🔴 «БОТ ЗАВИС — рестартую»; ескалації 🆘 «Рестарт не допоміг» і 🔴 «потрібні руки». rationale: авторестарт не повторюється в 30-хв кулдауні, щоб не маскувати системну проблему петлею перезапусків, Щоденні команди: logs -f bot, logs | tail -30, compose down, бекап cp data/bot.db ~/backup-recipes-$(date +%F).db, scripts/deploy.sh (git pull + rebuild). rationale: --build обов'язковий — без нього up -d бере старий образ і бот мовчки працює на старому коді (крешлуп після git pull), .env-ключі: BOT_TOKEN, OPENROUTER_API_KEY (основний LLM), GEMINI_API_KEY (запасний), OPENROUTER_MODEL (google/gemini-3.1-flash-lite-preview), ALLOWED_USER_IDS, ADMIN_USER_IDS. Потрібен хоча б один LLM-ключ, Правило зміни .env: docker compose up -d, НЕ restart. rationale: restart не перечитує env_file — змінні вшиваються при створенні контейнера; up -d помічає зміну і перестворює його (+13 more)

### Community 15 - "Telegram Input Ingestion"
Cohesion: 0.21
Nodes (17): AsyncFunctionDef, FunctionDef, Module, _imported_modules(), _imported_names_from(), _is_property(), _is_trivial_property(), _parse() (+9 more)

### Community 16 - "Initial Schema Migration"
Cohesion: 0.25
Nodes (12): aggregate(), _format_amount(), parse_qty(), Агрегація інгредієнтів у список покупок., «1,5» → 1.5; «1/2» → 0.5; «2-3» → 3 (беремо більше, щоб точно вистачило)., Сумує кількості за (назва, одиниця). Повертає готові рядки списку покупок., test_aggregate_decimal_comma_output(), test_aggregate_keeps_different_units_separate() (+4 more)

### Community 17 - "Aiogram Bot Symbol"
Cohesion: 0.28
Nodes (9): services/ingestion.py adapter (sanctioned aiogram exception), Layer Rules (handlers → services → repo → models), Rule 1: Models are data-only, Rule 6: New feature = new service, Rule 2: repo.py is the single SQL point, Rule 3: Services know nothing about Telegram, Architecture Test Suite (tests/test_architecture.py), Rule 4: Thin handlers (no SQL, no business rules, no prompts) (+1 more)

### Community 18 - "Package Init"
Cohesion: 0.36
Nodes (7): collect_input(), _download(), Bot, Message, Перетворення повідомлення Telegram на вхід для екстракції рецепта., Витягує текст і файли з повідомлення (фото/скрін/PDF/текст/форвард)., RecipeInput

### Community 19 - "Recipe Model Reference"
Cohesion: 0.67
Nodes (4): Deploy Concurrency Gate, SSH Deploy Job, Test & Deploy GitHub Actions Workflow, CI Test Job (uv sync + pytest)

### Community 20 - "Package Init"
Cohesion: 0.50
Nodes (4): .github/workflows/deploy.yml — Test & Deploy workflow (push to main + workflow_dispatch), GitHub Actions autodeploy setup (deploy key + 4 secrets + workflow_dispatch smoke test), systemd reads watcher scripts straight from the git working tree, so git merge auto-updates them (unit files excepted — need re-copy + daemon-reload), scripts/deploy.sh — git ff-merge + compose up -d --build

### Community 21 - "LLMClient Reference"
Cohesion: 0.83
Nodes (3): notify(), ntfy-docker-watch.sh script, wait_ready()

## Knowledge Gaps
- **19 isolated node(s):** `tg-bot-sho-poisty (project)`, `deploy.sh script`, `ntfy-send.sh script`, `server-maint.sh script`, `check-heartbeat.sh script` (+14 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **35 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `New-server-from-scratch checklist (8 ordered steps)` connect `Recipe Adding Handlers` to `Recipe Rendering`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `LLMClient` (e.g. with `AddStates` and `GeminiClient`) actually correct?**
  _`LLMClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `tg-bot-sho-poisty (project)`, `deploy.sh script`, `ntfy-send.sh script` to the rest of the system?**
  _19 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `LLM Contract & Schemas` be split into smaller, more focused modules?**
  _Cohesion score 0.09711538461538462 - nodes in this community are weakly interconnected._
- **Should `Architecture Rules & Guidelines` be split into smaller, more focused modules?**
  _Cohesion score 0.06497175141242938 - nodes in this community are weakly interconnected._
- **Should `Dish Query Handlers` be split into smaller, more focused modules?**
  _Cohesion score 0.09724238026124818 - nodes in this community are weakly interconnected._
- **Should `Repository SQL Layer` be split into smaller, more focused modules?**
  _Cohesion score 0.1024390243902439 - nodes in this community are weakly interconnected._