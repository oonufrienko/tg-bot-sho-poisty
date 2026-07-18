# Graph Report - .  (2026-07-18)

## Corpus Check
- 2 files · ~20,535 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 618 nodes · 1236 edges · 66 communities (31 shown, 35 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 49 edges (avg confidence: 0.66)
- Token cost: 66,175 input · 0 output

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
- Community 41
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47
- Community 48
- Community 49
- Community 50
- Community 52
- Community 54
- Community 56
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
- `test_parse_qty_variants()` --calls--> `parse_qty()`  [EXTRACTED]
  tests/test_shopping_list.py → bot/services/shopping_list.py
- `test_aggregate_decimal_comma_output()` --calls--> `aggregate()`  [EXTRACTED]
  tests/test_shopping_list.py → bot/services/shopping_list.py
- `test_aggregate_keeps_different_units_separate()` --calls--> `aggregate()`  [EXTRACTED]
  tests/test_shopping_list.py → bot/services/shopping_list.py
- `test_aggregate_mixed_parsed_and_note_for_same_name()` --calls--> `aggregate()`  [EXTRACTED]
  tests/test_shopping_list.py → bot/services/shopping_list.py
- `test_aggregate_sums_same_ingredient_and_unit()` --calls--> `aggregate()`  [EXTRACTED]
  tests/test_shopping_list.py → bot/services/shopping_list.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Preferred DB restore path: shutdown old bot, checkpoint WAL, scp** — install_old_bot_shutdown, install_scp_bot_db, install_db_restore [EXTRACTED 1.00]
- **Backup pipeline: checkpoint, encrypt, upload** — runbook_wal_checkpoint, runbook_age_encryption, runbook_r2_upload [EXTRACTED 1.00]
- **Backup reliability safeguards** — runbook_ntfy_failure_alert, runbook_healthchecks_dead_man_switch, runbook_cron_schedule [EXTRACTED 1.00]
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
Cohesion: 0.05
Nodes (49): docker-compose bot Service, json-file Log Rotation Limits, stop_grace_period 30s for aiogram Shutdown, Restore database before first start (step 4), scripts/deploy.sh, Docker + compose service enabled, docker-image-prune.timer, docker compose up -d --build (first start) (+41 more)

### Community 3 - "Repository SQL Layer"
Cohesion: 0.13
Nodes (26): ABC, BaseModel, Recipe, ExtractedIngredient, LLMClient, MenuPlanResult, MenuSlot, QueryIntent (+18 more)

### Community 4 - "Group Management Handlers"
Cohesion: 0.08
Nodes (23): Any, async_sessionmaker, BaseMiddleware, BaseSettings, get_settings(), Відкритий доступ — лише за явним ALLOWED_USER_IDS=* (dev-режим)., Адміни бачать «Статистика». Без '*'-магії: порожнє = адмінів немає., Settings (+15 more)

### Community 5 - "ORM Models & Repo Tests"
Cohesion: 0.11
Nodes (36): add_recipe(), clear_served(), count_users(), create_group(), delete_recipe(), ensure_user(), find_recipe_by_title(), get_group() (+28 more)

### Community 6 - "Recipe Adding Handlers"
Cohesion: 0.17
Nodes (22): AsyncSession, User, add_hint(), AddStates, amend_apply(), handle_media(), Спільний вхід: екстракція + картка підтвердження., save_recipe() (+14 more)

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
Cohesion: 0.11
Nodes (23): Definition of Done, Goal-Driven Execution, Knowledge Graph Freshness Rule, Layer Rules (ARCHITECTURE.md), Simplicity First, Surgical Changes, tg-bot-sho-poisty (project), CodeRabbit Review Configuration (+15 more)

### Community 12 - "Shopping List Aggregation"
Cohesion: 0.14
Nodes (22): README.md — Що поїсти? bot overview, Auto-deploy: push to main runs tests and deploys via GitHub Actions over SSH executing scripts/deploy.sh, Categories: breakfast, lunch, dinner, dessert, salad, general (+ difficulty 1-4), DB reset procedure: down, backup bot.db, rm, up --build (migrations recreate empty DB), Dish selection queries (what's for dinner, from chicken, etc.), Docker run on server: docker compose up -d --build, Gemini API (free fallback, GEMINI_API_KEY, ~10 req/min free tier), Recommended workflow: create group and make it active before uploading recipes; bot offers transfer otherwise (+14 more)

### Community 13 - "Deployment & Secrets"
Cohesion: 0.20
Nodes (16): Base, Group, GroupMember, RecipeCategory, RecipeMedia, ServeHistory, utcnow(), Останні рекомендовані за датами (свіжа зверху): (ServeHistory, Recipe). (+8 more)

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
Cohesion: 0.31
Nodes (12): _by_category(), Групує за першою категорією рецепта, секції у порядку CATEGORIES., Список за категоріями. Повертає (текст, id у порядку нумерації)., render_recipe_list(), make(), render_recipe_list: групування за категоріями та наскрізна нумерація., test_difficulty_rendered_as_stars(), test_multi_category_recipe_shown_once_under_first_category() (+4 more)

### Community 18 - "Package Init"
Cohesion: 0.28
Nodes (9): services/ingestion.py adapter (sanctioned aiogram exception), Layer Rules (handlers → services → repo → models), Rule 1: Models are data-only, Rule 6: New feature = new service, Rule 2: repo.py is the single SQL point, Rule 3: Services know nothing about Telegram, Architecture Test Suite (tests/test_architecture.py), Rule 4: Thin handlers (no SQL, no business rules, no prompts) (+1 more)

### Community 19 - "Recipe Model Reference"
Cohesion: 0.36
Nodes (7): collect_input(), _download(), Bot, Message, Перетворення повідомлення Telegram на вхід для екстракції рецепта., Витягує текст і файли з повідомлення (фото/скрін/PDF/текст/форвард)., RecipeInput

### Community 20 - "Package Init"
Cohesion: 0.67
Nodes (4): Deploy Concurrency Gate, SSH Deploy Job, Test & Deploy GitHub Actions Workflow, CI Test Job (uv sync + pytest)

### Community 21 - "LLMClient Reference"
Cohesion: 0.83
Nodes (3): notify(), ntfy-docker-watch.sh script, wait_ready()

## Knowledge Gaps
- **26 isolated node(s):** `tg-bot-sho-poisty (project)`, `deploy.sh script`, `ntfy-send.sh script`, `server-maint.sh script`, `check-heartbeat.sh script` (+21 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **35 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_parse()` connect `Telegram Input Ingestion` to `Group Management Handlers`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Why does `OpenRouterClient` connect `LLM Errors & Retry` to `LLM Contract & Schemas`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `LLMClient` (e.g. with `AddStates` and `GeminiClient`) actually correct?**
  _`LLMClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `tg-bot-sho-poisty (project)`, `deploy.sh script`, `ntfy-send.sh script` to the rest of the system?**
  _26 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `LLM Contract & Schemas` be split into smaller, more focused modules?**
  _Cohesion score 0.09711538461538462 - nodes in this community are weakly interconnected._
- **Should `Architecture Rules & Guidelines` be split into smaller, more focused modules?**
  _Cohesion score 0.06497175141242938 - nodes in this community are weakly interconnected._
- **Should `Dish Query Handlers` be split into smaller, more focused modules?**
  _Cohesion score 0.05357142857142857 - nodes in this community are weakly interconnected._