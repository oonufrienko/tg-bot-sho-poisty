# Graph Report - .  (2026-07-15)

## Corpus Check
- 24 files · ~14,197 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 415 nodes · 914 edges · 37 communities (24 shown, 13 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 48 edges (avg confidence: 0.67)
- Token cost: 55,981 input · 0 output

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
- Aiogram Bot Symbol
- Recipe Model Reference
- LLMClient Reference
- QueryIntent Reference
- LLMClient Reference
- QueryIntent Reference
- Keyboard Markup Reference
- DishCB Callback Reference
- Exception Reference
- Group Model Reference
- Project Root Node
- RecentCB Callback Reference
- Generic TypeVar

## God Nodes (most connected - your core abstractions)
1. `LLMClient` - 30 edges
2. `QueryIntent` - 23 edges
3. `OpenRouterClient` - 18 edges
4. `LLMError` - 14 edges
5. `GeminiClient` - 14 edges
6. `run_with_retries()` - 14 edges
7. `LLMQuotaError` - 13 edges
8. `run_find_dish()` - 12 edges
9. `free_text()` - 12 edges
10. `RecipeExtraction` - 12 edges

## Surprising Connections (you probably didn't know these)
- `bot service` --references--> `.env File on Server`  [INFERRED]
  docker-compose.yml → NEXT_STEPS.md
- `Layer Rules Enforced By Architecture Tests` --conceptually_related_to--> `CodeRabbit Review Configuration`  [INFERRED]
  CLAUDE.md → .coderabbit.yaml
- `test_parse_qty_variants()` --calls--> `parse_qty()`  [EXTRACTED]
  tests/test_shopping_list.py → bot/services/shopping_list.py
- `test_aggregate_decimal_comma_output()` --calls--> `aggregate()`  [EXTRACTED]
  tests/test_shopping_list.py → bot/services/shopping_list.py
- `test_aggregate_keeps_different_units_separate()` --calls--> `aggregate()`  [EXTRACTED]
  tests/test_shopping_list.py → bot/services/shopping_list.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Layer Boundary Rules Enforced Across Config, Docs And Tests** — coderabbit_models_data_only_rule, coderabbit_repo_sole_query_site_rule, coderabbit_thin_handlers_rule, coderabbit_services_tenancy_explicit_rule, claude_layer_rules_enforced_by_tests [INFERRED 0.85]
- **Group Tenancy Isolation Concerns** — readme_group_shared_recipe_base, report_2026_07_14_09_01_cross_group_serve_history, report_2026_07_14_09_01_fsm_group_binding, report_2026_07_14_09_01_group_scoping_invariant, coderabbit_services_tenancy_explicit_rule [INFERRED 0.85]
- **Zero-Hallucination Enforcement Mechanisms** — readme_zero_hallucination_principle, coderabbit_llm_escaping_rule, coderabbit_llmclient_interface_rule, readme_shopping_list_scaling_limitation [INFERRED 0.85]
- **Layered Architecture Rule Set** — architecture_layer_rules, architecture_models_data_only, architecture_repo_single_sql_point, architecture_services_no_telegram, architecture_thin_handlers, architecture_new_feature_new_service [EXTRACTED 1.00]
- **Server .env Configuration Bundle** — next_steps_env_file, next_steps_bot_token, next_steps_gemini_api_key, next_steps_allowed_user_ids [EXTRACTED 1.00]

## Communities (37 total, 13 thin omitted)

### Community 0 - "LLM Contract & Schemas"
Cohesion: 0.12
Nodes (27): ABC, BaseModel, Recipe, ExtractedIngredient, LLMClient, MenuPlanResult, MenuSlot, QueryIntent (+19 more)

### Community 1 - "Architecture Rules & Guidelines"
Cohesion: 0.07
Nodes (41): services/ingestion.py adapter (sanctioned aiogram exception), Layer Rules (handlers → services → repo → models), Rule 1: Models are data-only, Rule 6: New feature = new service, Rule 2: repo.py is the single SQL point, Rule 3: Services know nothing about Telegram, Architecture Test Suite (tests/test_architecture.py), Rule 4: Thin handlers (no SQL, no business rules, no prompts) (+33 more)

### Community 2 - "Dish Query Handlers"
Cohesion: 0.16
Nodes (36): another_dish(), ask_delete(), ask_hint(), ask_suggestion(), cancel_delete(), choose_dish(), confirm_delete(), free_text() (+28 more)

### Community 3 - "Repository SQL Layer"
Cohesion: 0.13
Nodes (32): add_recipe(), create_group(), delete_recipe(), ensure_user(), find_recipe_by_title(), get_group(), get_recipe(), get_user() (+24 more)

### Community 4 - "Group Management Handlers"
Cohesion: 0.14
Nodes (31): create_group_finish(), create_group_start(), group_menu(), _group_overview(), GroupStates, invite_link(), members_list(), move_recipes_confirm() (+23 more)

### Community 5 - "ORM Models & Repo Tests"
Cohesion: 0.11
Nodes (26): Base, Group, GroupMember, RecipeCategory, RecipeMedia, ServeHistory, User, utcnow() (+18 more)

### Community 6 - "Recipe Adding Handlers"
Cohesion: 0.15
Nodes (26): add_hint(), AddStates, amend_apply(), amend_start(), cancel(), handle_media(), AsyncSession, Bot (+18 more)

### Community 7 - "Config, Session & Migrations"
Cohesion: 0.12
Nodes (15): Any, async_sessionmaker, BaseMiddleware, BaseSettings, get_settings(), Відкритий доступ — лише за явним ALLOWED_USER_IDS=* (dev-режим)., Settings, get_session_factory() (+7 more)

### Community 8 - "LLM Errors & Retry"
Cohesion: 0.16
Nodes (22): LLMError, LLMQuotaError, Exception, Перевищено ліміт запитів провайдера (HTTP 429)., Exception, T, Спільні ретраї для LLM-провайдерів з класифікацією за HTTP-статусом., Пауза перед наступною спробою; None = помилка постійна, не ретраїмо. (+14 more)

### Community 9 - "Architecture Test Internals"
Cohesion: 0.19
Nodes (18): AsyncFunctionDef, FunctionDef, Module, Path, _imported_modules(), _imported_names_from(), _is_property(), _is_trivial_property() (+10 more)

### Community 10 - "OpenRouter Client"
Cohesion: 0.20
Nodes (10): _file_part(), OpenRouterClient, T, _text_part(), _client_with_stub(), OpenRouterClient: збірка повідомлення і параметрів без реальних викликів API., StubCompletions, test_extract_recipe_builds_multimodal_message() (+2 more)

### Community 11 - "Menu Planning Handlers"
Cohesion: 0.35
Nodes (13): menu_hint(), _plan_for_active_group(), AsyncSession, CallbackQuery, FSMContext, Message, User, run_menu_flow() (+5 more)

### Community 12 - "Shopping List Aggregation"
Cohesion: 0.25
Nodes (12): aggregate(), _format_amount(), parse_qty(), Агрегація інгредієнтів у список покупок., «1,5» → 1.5; «1/2» → 0.5; «2-3» → 3 (беремо більше, щоб точно вистачило)., Сумує кількості за (назва, одиниця). Повертає готові рядки списку покупок., test_aggregate_decimal_comma_output(), test_aggregate_keeps_different_units_separate() (+4 more)

### Community 13 - "Deployment & Secrets"
Cohesion: 0.20
Nodes (10): bot service, ./data Volume Mount, ALLOWED_USER_IDS (whitelist env var, fail-closed), BOT_TOKEN, BotFather, Deployment Workflow (docker compose, rsync update), .env File on Server, GEMINI_API_KEY (+2 more)

### Community 14 - "Recipe Rendering"
Cohesion: 0.39
Nodes (6): _ingredient_line(), Recipe, Формування текстів відповідей. Рецепти рендеряться ДОСЛІВНО з БД., render_extraction_card(), render_menu_day(), render_recipe()

### Community 15 - "Telegram Input Ingestion"
Cohesion: 0.36
Nodes (7): collect_input(), _download(), Bot, Message, Перетворення повідомлення Telegram на вхід для екстракції рецепта., Витягує текст і файли з повідомлення (фото/скрін/PDF/текст/форвард)., RecipeInput

## Knowledge Gaps
- **6 isolated node(s):** `./data Volume Mount`, `GEMINI_API_KEY`, `BotFather`, `userinfobot`, `Oracle Server (ssh ubuntu@oracle, ~/tg-bot-sho-poisty)` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LLMClient` connect `LLM Contract & Schemas` to `Dish Query Handlers`, `Recipe Adding Handlers`, `Config, Session & Migrations`, `OpenRouter Client`, `Menu Planning Handlers`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `OpenRouterClient` connect `OpenRouter Client` to `LLM Contract & Schemas`, `LLM Errors & Retry`, `Config, Session & Migrations`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Why does `LLMError` connect `LLM Errors & Retry` to `LLM Contract & Schemas`, `Dish Query Handlers`, `Recipe Adding Handlers`, `OpenRouter Client`, `Menu Planning Handlers`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `LLMClient` (e.g. with `AddStates` and `GeminiClient`) actually correct?**
  _`LLMClient` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `QueryIntent` (e.g. with `GeminiClient` and `OpenRouterClient`) actually correct?**
  _`QueryIntent` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `OpenRouterClient` (e.g. with `LLMClient` and `LLMError`) actually correct?**
  _`OpenRouterClient` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `LLMError` (e.g. with `AddStates` and `OpenRouterClient`) actually correct?**
  _`LLMError` has 4 INFERRED edges - model-reasoned connections that need verification._