# Graph Report - .  (2026-07-17)

## Corpus Check
- 3 files · ~19,498 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 545 nodes · 1110 edges · 47 communities (26 shown, 21 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 45 edges (avg confidence: 0.68)
- Token cost: 54,333 input · 0 output

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
- Recipe Model Reference
- Package Init
- LLMClient Reference
- LLMClient Reference
- Package Init
- Keyboard Markup Reference
- Package Init
- Package Init
- Package Init
- DishCB Callback Reference
- Exception Reference
- Group Model Reference
- RecentCB Callback Reference
- Community 38
- Community 39
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45

## God Nodes (most connected - your core abstractions)
1. `QueryIntent` - 17 edges
2. `LLMClient` - 17 edges
3. `_make_user_with_recipe()` - 16 edges
4. `render_recipe_list()` - 13 edges
5. `GeminiClient` - 12 edges
6. `run_with_retries()` - 12 edges
7. `run_find_dish()` - 12 edges
8. `Recipe` - 11 edges
9. `OpenRouterClient` - 11 edges
10. `recent_list()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Green 'bot up' alert means really working: watcher waits up to 90s for fresh heartbeat, otherwise sends 'bot did not show up for work'` --references--> `heartbeat_loop()`  [EXTRACTED]
  RUNBOOK.md → bot/main.py
- `stop_grace_period 30s for aiogram Shutdown` --conceptually_related_to--> `ntfy-bot-watch.service — listens to docker events, sends crash/stop/up alerts`  [INFERRED]
  docker-compose.yml → INSTALL.md
- `heartbeat_loop()` --shares_data_with--> `scripts/check-heartbeat.sh — heartbeat freshness check + auto-restart`  [EXTRACTED]
  bot/main.py → INSTALL.md
- `INSTALL.md — server installation guide (bot, watchers, autodeploy)` --references--> `heartbeat_loop()`  [EXTRACTED]
  INSTALL.md → bot/main.py
- `RUNBOOK.md — day-to-day operations cheat sheet` --references--> `heartbeat_loop()`  [EXTRACTED]
  RUNBOOK.md → bot/main.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Hang detection and auto-restart chain: bot heartbeat → timer check → restart → ntfy alerts** — bot_main_heartbeat_loop, install_ntfy_heartbeat_check_timer, scripts_check_heartbeat_sh, runbook_heartbeat_state_files, scripts_ntfy_send [EXTRACTED 1.00]
- **Host-side systemd watcher suite living outside Docker** — install_ntfy_bot_watch_service, install_ntfy_heartbeat_check_timer, install_ntfy_disk_check_timer, install_docker_image_prune_timer, install_ntfy_bot_watch_env [EXTRACTED 1.00]
- **Autodeploy pipeline: merge to main → GitHub Actions → SSH → deploy.sh** — github_workflows_deploy, scripts_deploy_sh, install_autodeploy_setup [EXTRACTED 1.00]
- **Automated Deploy Pipeline (push main -> test -> SSH deploy -> compose rebuild)** — _github_workflows_deploy_test_job, _github_workflows_deploy_deploy_job, docker_compose_bot_service, runbook_operations_runbook [EXTRACTED 1.00]
- **Layer Boundary Rules Enforced Across Config, Docs And Tests** — coderabbit_models_data_only_rule, coderabbit_repo_sole_query_site_rule, coderabbit_thin_handlers_rule, coderabbit_services_tenancy_explicit_rule, claude_layer_rules_enforced_by_tests [INFERRED 0.85]
- **Group Tenancy Isolation Concerns** — readme_group_shared_recipe_base, report_2026_07_14_09_01_cross_group_serve_history, report_2026_07_14_09_01_fsm_group_binding, report_2026_07_14_09_01_group_scoping_invariant, coderabbit_services_tenancy_explicit_rule [INFERRED 0.85]
- **Layered Architecture Rule Set** — architecture_layer_rules, architecture_models_data_only, architecture_repo_single_sql_point, architecture_services_no_telegram, architecture_thin_handlers, architecture_new_feature_new_service [EXTRACTED 1.00]

## Communities (47 total, 21 thin omitted)

### Community 0 - "LLM Contract & Schemas"
Cohesion: 0.10
Nodes (59): Bot, another_dish(), apply_edit(), ask_delete_number(), ask_edit_number(), ask_hint(), _ask_number(), ask_suggestion() (+51 more)

### Community 1 - "Architecture Rules & Guidelines"
Cohesion: 0.06
Nodes (44): heartbeat_loop(), main(), Пише unix-час у файл; якщо event loop завис — файл стає застарілим.      Свіжіст, run_migrations(), docker-compose bot Service, json-file Log Rotation Limits, stop_grace_period 30s for aiogram Shutdown, .github/workflows/deploy.yml — Test & Deploy workflow (push to main + workflow_dispatch) (+36 more)

### Community 2 - "Dish Query Handlers"
Cohesion: 0.09
Nodes (37): Base, Group, GroupMember, RecipeCategory, RecipeMedia, ServeHistory, User, utcnow() (+29 more)

### Community 3 - "Repository SQL Layer"
Cohesion: 0.13
Nodes (26): ABC, BaseModel, Recipe, ExtractedIngredient, LLMClient, MenuPlanResult, MenuSlot, QueryIntent (+18 more)

### Community 4 - "Group Management Handlers"
Cohesion: 0.12
Nodes (34): add_recipe(), clear_served(), create_group(), delete_recipe(), ensure_user(), find_recipe_by_title(), get_group(), get_recipe() (+26 more)

### Community 5 - "ORM Models & Repo Tests"
Cohesion: 0.14
Nodes (31): create_group_finish(), create_group_start(), group_menu(), _group_overview(), GroupStates, invite_link(), members_list(), move_recipes_confirm() (+23 more)

### Community 6 - "Recipe Adding Handlers"
Cohesion: 0.11
Nodes (14): Any, async_sessionmaker, BaseMiddleware, BaseSettings, get_settings(), Відкритий доступ — лише за явним ALLOWED_USER_IDS=* (dev-режим)., Settings, get_session_factory() (+6 more)

### Community 7 - "Config, Session & Migrations"
Cohesion: 0.16
Nodes (22): LLMError, LLMQuotaError, Exception, Перевищено ліміт запитів провайдера (HTTP 429)., Exception, T, Спільні ретраї для LLM-провайдерів з класифікацією за HTTP-статусом., Пауза перед наступною спробою; None = помилка постійна, не ретраїмо. (+14 more)

### Community 8 - "LLM Errors & Retry"
Cohesion: 0.14
Nodes (14): _file_part(), OpenRouterClient, LLM-клієнт через OpenRouter (OpenAI-сумісний API).  Використовується, коли задан, _text_part(), MenuPlanResult, RecipeExtraction, SelectionResult, T (+6 more)

### Community 9 - "Architecture Test Internals"
Cohesion: 0.11
Nodes (15): _extraction(), _LLM, _Msg, _NoopTyping, Message, _Query, Звʼязка «редагування → картка → Зберегти».  Ці інваріанти живуть у передачі edit, Саме тут ховався баг: картка губила edit_id і «Зберегти» робило копію. (+7 more)

### Community 10 - "OpenRouter Client"
Cohesion: 0.20
Nodes (23): add_hint(), AddStates, amend_apply(), amend_start(), cancel(), handle_media(), AsyncSession, Bot (+15 more)

### Community 11 - "Menu Planning Handlers"
Cohesion: 0.15
Nodes (21): _make_user_with_recipe(), Правка міняє текст рецепта, а не його походження чи історію подач., Сценарій бага: створив нову групу → переніс рецепти → запрошений їх бачить., Дублікат за назвою (інший регістр/пробіли) лишається у старій групі., recipe_id з callback-data не має відкривати рецепти чужої групи., ServeHistory має FK на recipes.id без cascade — історію треба прибрати явно., test_category_filter(), test_clear_served_wipes_history_for_group_only() (+13 more)

### Community 12 - "Shopping List Aggregation"
Cohesion: 0.11
Nodes (22): Definition of Done, Goal-Driven Execution, Knowledge Graph Freshness Rule, Layer Rules (ARCHITECTURE.md), Simplicity First, Surgical Changes, tg-bot-sho-poisty (project), CodeRabbit Review Configuration (+14 more)

### Community 13 - "Deployment & Secrets"
Cohesion: 0.12
Nodes (19): Deploy Concurrency Gate, SSH Deploy Job, Test & Deploy GitHub Actions Workflow, CI Test Job (uv sync + pytest), services/ingestion.py adapter (sanctioned aiogram exception), Layer Rules (handlers → services → repo → models), Rule 1: Models are data-only, Rule 6: New feature = new service (+11 more)

### Community 14 - "Recipe Rendering"
Cohesion: 0.22
Nodes (17): menu_hint(), _plan_for_active_group(), AsyncSession, CallbackQuery, FSMContext, Message, User, run_menu_flow() (+9 more)

### Community 15 - "Telegram Input Ingestion"
Cohesion: 0.21
Nodes (17): AsyncFunctionDef, FunctionDef, Module, _imported_modules(), _imported_names_from(), _is_property(), _is_trivial_property(), _parse() (+9 more)

### Community 16 - "Initial Schema Migration"
Cohesion: 0.25
Nodes (12): aggregate(), _format_amount(), parse_qty(), Агрегація інгредієнтів у список покупок., «1,5» → 1.5; «1/2» → 0.5; «2-3» → 3 (беремо більше, щоб точно вистачило)., Сумує кількості за (назва, одиниця). Повертає готові рядки списку покупок., test_aggregate_decimal_comma_output(), test_aggregate_keeps_different_units_separate() (+4 more)

### Community 17 - "Aiogram Bot Symbol"
Cohesion: 0.36
Nodes (7): collect_input(), _download(), Bot, Message, Перетворення повідомлення Telegram на вхід для екстракції рецепта., Витягує текст і файли з повідомлення (фото/скрін/PDF/текст/форвард)., RecipeInput

## Knowledge Gaps
- **9 isolated node(s):** `tg-bot-sho-poisty`, `tg-bot-sho-poisty (project)`, `deploy.sh script`, `ntfy-send.sh script`, `server-maint.sh script` (+4 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_parse()` connect `Telegram Input Ingestion` to `Architecture Rules & Guidelines`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **What connects `tg-bot-sho-poisty`, `tg-bot-sho-poisty (project)`, `deploy.sh script` to the rest of the system?**
  _9 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `LLM Contract & Schemas` be split into smaller, more focused modules?**
  _Cohesion score 0.10087045570916539 - nodes in this community are weakly interconnected._
- **Should `Architecture Rules & Guidelines` be split into smaller, more focused modules?**
  _Cohesion score 0.05612244897959184 - nodes in this community are weakly interconnected._
- **Should `Dish Query Handlers` be split into smaller, more focused modules?**
  _Cohesion score 0.08970099667774087 - nodes in this community are weakly interconnected._
- **Should `Repository SQL Layer` be split into smaller, more focused modules?**
  _Cohesion score 0.12560975609756098 - nodes in this community are weakly interconnected._
- **Should `Group Management Handlers` be split into smaller, more focused modules?**
  _Cohesion score 0.1226890756302521 - nodes in this community are weakly interconnected._