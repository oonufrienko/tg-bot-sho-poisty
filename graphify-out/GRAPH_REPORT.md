# Graph Report - .  (2026-07-16)

## Corpus Check
- 20 files · ~18,670 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 528 nodes · 1090 edges · 48 communities (26 shown, 22 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 44 edges (avg confidence: 0.68)
- Token cost: 52,878 input · 0 output

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
- QueryIntent Reference
- QueryIntent Reference
- Keyboard Markup Reference
- Package Init
- Package Init
- Package Init
- DishCB Callback Reference
- Exception Reference
- Group Model Reference
- Project Root Node
- Generic TypeVar
- Community 39
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46

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
- `Whitelist Fail-Closed Access Control` --semantically_similar_to--> `ntfy Topic as Shared Secret`  [INFERRED] [semantically similar]
  README.md → INSTALL.md
- `test_parse_qty_variants()` --calls--> `parse_qty()`  [EXTRACTED]
  tests/test_shopping_list.py → bot/services/shopping_list.py
- `test_aggregate_decimal_comma_output()` --calls--> `aggregate()`  [EXTRACTED]
  tests/test_shopping_list.py → bot/services/shopping_list.py
- `test_aggregate_keeps_different_units_separate()` --calls--> `aggregate()`  [EXTRACTED]
  tests/test_shopping_list.py → bot/services/shopping_list.py
- `test_aggregate_mixed_parsed_and_note_for_same_name()` --calls--> `aggregate()`  [EXTRACTED]
  tests/test_shopping_list.py → bot/services/shopping_list.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **ntfy Monitoring Stack** — install_ntfy_bot_watch_service, install_ntfy_heartbeat_check_timer, install_ntfy_disk_check_timer, install_docker_image_prune_timer, runbook_heartbeat_autorestart [EXTRACTED 1.00]
- **Automated Deploy Pipeline (push main -> test -> SSH deploy -> compose rebuild)** — _github_workflows_deploy_test_job, _github_workflows_deploy_deploy_job, docker_compose_bot_service, runbook_operations_runbook [EXTRACTED 1.00]
- **Disk Hygiene on 45 GB / 1 GB RAM Server** — docker_compose_log_rotation, install_ntfy_disk_check_timer, install_docker_image_prune_timer [INFERRED 0.85]
- **Layer Boundary Rules Enforced Across Config, Docs And Tests** — coderabbit_models_data_only_rule, coderabbit_repo_sole_query_site_rule, coderabbit_thin_handlers_rule, coderabbit_services_tenancy_explicit_rule, claude_layer_rules_enforced_by_tests [INFERRED 0.85]
- **Group Tenancy Isolation Concerns** — readme_group_shared_recipe_base, report_2026_07_14_09_01_cross_group_serve_history, report_2026_07_14_09_01_fsm_group_binding, report_2026_07_14_09_01_group_scoping_invariant, coderabbit_services_tenancy_explicit_rule [INFERRED 0.85]
- **Layered Architecture Rule Set** — architecture_layer_rules, architecture_models_data_only, architecture_repo_single_sql_point, architecture_services_no_telegram, architecture_thin_handlers, architecture_new_feature_new_service [EXTRACTED 1.00]

## Communities (48 total, 22 thin omitted)

### Community 0 - "LLM Contract & Schemas"
Cohesion: 0.11
Nodes (57): Bot, another_dish(), apply_edit(), ask_delete_number(), ask_edit_number(), ask_hint(), _ask_number(), ask_suggestion() (+49 more)

### Community 1 - "Architecture Rules & Guidelines"
Cohesion: 0.13
Nodes (26): ABC, BaseModel, Recipe, ExtractedIngredient, LLMClient, MenuPlanResult, MenuSlot, QueryIntent (+18 more)

### Community 2 - "Dish Query Handlers"
Cohesion: 0.09
Nodes (22): Any, async_sessionmaker, BaseMiddleware, BaseSettings, get_settings(), Відкритий доступ — лише за явним ALLOWED_USER_IDS=* (dev-режим)., Settings, get_session_factory() (+14 more)

### Community 3 - "Repository SQL Layer"
Cohesion: 0.12
Nodes (34): add_recipe(), clear_served(), create_group(), delete_recipe(), ensure_user(), find_recipe_by_title(), get_group(), get_recipe() (+26 more)

### Community 4 - "Group Management Handlers"
Cohesion: 0.07
Nodes (33): services/ingestion.py adapter (sanctioned aiogram exception), Layer Rules (handlers → services → repo → models), Rule 1: Models are data-only, Rule 6: New feature = new service, Rule 2: repo.py is the single SQL point, Rule 3: Services know nothing about Telegram, Architecture Test Suite (tests/test_architecture.py), Rule 4: Thin handlers (no SQL, no business rules, no prompts) (+25 more)

### Community 5 - "ORM Models & Repo Tests"
Cohesion: 0.14
Nodes (31): create_group_finish(), create_group_start(), group_menu(), _group_overview(), GroupStates, invite_link(), members_list(), move_recipes_confirm() (+23 more)

### Community 6 - "Recipe Adding Handlers"
Cohesion: 0.13
Nodes (27): _by_category(), _ingredient_line(), Recipe, Формування текстів відповідей. Рецепти рендеряться ДОСЛІВНО з БД., Групує за першою категорією рецепта, секції у порядку CATEGORIES., Список за категоріями. Повертає (текст, id у порядку нумерації)., Останні рекомендовані страви за категоріями: (ServeHistory, Recipe)., render_extraction_card() (+19 more)

### Community 7 - "Config, Session & Migrations"
Cohesion: 0.15
Nodes (27): add_hint(), AddStates, amend_apply(), amend_start(), cancel(), handle_media(), AsyncSession, Bot (+19 more)

### Community 8 - "LLM Errors & Retry"
Cohesion: 0.13
Nodes (16): _meal_type(), _file_part(), OpenRouterClient, LLM-клієнт через OpenRouter (OpenAI-сумісний API).  Використовується, коли задан, _text_part(), MenuPlanResult, QueryIntent, RecipeExtraction (+8 more)

### Community 9 - "Architecture Test Internals"
Cohesion: 0.16
Nodes (23): Base, Group, GroupMember, RecipeCategory, RecipeMedia, ServeHistory, User, utcnow() (+15 more)

### Community 10 - "OpenRouter Client"
Cohesion: 0.16
Nodes (22): LLMError, LLMQuotaError, Exception, Перевищено ліміт запитів провайдера (HTTP 429)., Exception, T, Спільні ретраї для LLM-провайдерів з класифікацією за HTTP-статусом., Пауза перед наступною спробою; None = помилка постійна, не ретраїмо. (+14 more)

### Community 11 - "Menu Planning Handlers"
Cohesion: 0.11
Nodes (15): _extraction(), _LLM, _Msg, _NoopTyping, Message, _Query, Звʼязка «редагування → картка → Зберегти».  Ці інваріанти живуть у передачі edit, Саме тут ховався баг: картка губила edit_id і «Зберегти» робило копію. (+7 more)

### Community 12 - "Shopping List Aggregation"
Cohesion: 0.11
Nodes (24): Deploy Concurrency Gate, SSH Deploy Job, Test & Deploy GitHub Actions Workflow, CI Test Job (uv sync + pytest), docker-compose bot Service, json-file Log Rotation Limits, stop_grace_period 30s for aiogram Shutdown, docker-image-prune.timer (+16 more)

### Community 13 - "Deployment & Secrets"
Cohesion: 0.15
Nodes (21): _make_user_with_recipe(), Правка міняє текст рецепта, а не його походження чи історію подач., Сценарій бага: створив нову групу → переніс рецепти → запрошений їх бачить., Дублікат за назвою (інший регістр/пробіли) лишається у старій групі., recipe_id з callback-data не має відкривати рецепти чужої групи., ServeHistory має FK на recipes.id без cascade — історію треба прибрати явно., test_category_filter(), test_clear_served_wipes_history_for_group_only() (+13 more)

### Community 14 - "Recipe Rendering"
Cohesion: 0.21
Nodes (17): AsyncFunctionDef, FunctionDef, Module, _imported_modules(), _imported_names_from(), _is_property(), _is_trivial_property(), _parse() (+9 more)

### Community 15 - "Telegram Input Ingestion"
Cohesion: 0.25
Nodes (12): aggregate(), _format_amount(), parse_qty(), Агрегація інгредієнтів у список покупок., «1,5» → 1.5; «1/2» → 0.5; «2-3» → 3 (беремо більше, щоб точно вистачило)., Сумує кількості за (назва, одиниця). Повертає готові рядки списку покупок., test_aggregate_decimal_comma_output(), test_aggregate_keeps_different_units_separate() (+4 more)

### Community 16 - "Initial Schema Migration"
Cohesion: 0.36
Nodes (7): collect_input(), _download(), Bot, Message, Перетворення повідомлення Telegram на вхід для екстракції рецепта., Витягує текст і файли з повідомлення (фото/скрін/PDF/текст/форвард)., RecipeInput

### Community 17 - "Aiogram Bot Symbol"
Cohesion: 0.83
Nodes (3): notify(), ntfy-docker-watch.sh script, wait_ready()

## Knowledge Gaps
- **8 isolated node(s):** `tg-bot-sho-poisty`, `tg-bot-sho-poisty (project)`, `check-heartbeat.sh script`, `deploy.sh script`, `ntfy-send.sh script` (+3 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_parse()` connect `Recipe Rendering` to `Dish Query Handlers`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `OpenRouterClient` connect `LLM Errors & Retry` to `LLM Contract & Schemas`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **What connects `tg-bot-sho-poisty`, `tg-bot-sho-poisty (project)`, `check-heartbeat.sh script` to the rest of the system?**
  _8 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `LLM Contract & Schemas` be split into smaller, more focused modules?**
  _Cohesion score 0.10546448087431694 - nodes in this community are weakly interconnected._
- **Should `Architecture Rules & Guidelines` be split into smaller, more focused modules?**
  _Cohesion score 0.12560975609756098 - nodes in this community are weakly interconnected._
- **Should `Dish Query Handlers` be split into smaller, more focused modules?**
  _Cohesion score 0.08571428571428572 - nodes in this community are weakly interconnected._
- **Should `Repository SQL Layer` be split into smaller, more focused modules?**
  _Cohesion score 0.1226890756302521 - nodes in this community are weakly interconnected._