# Graph Report - .  (2026-07-15)

## Corpus Check
- 5 files · ~14,277 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 427 nodes · 908 edges · 38 communities (23 shown, 15 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 44 edges (avg confidence: 0.7)
- Token cost: 52,318 input · 0 output

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
- Initial Schema Migration
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
- Package Init

## God Nodes (most connected - your core abstractions)
1. `LLMClient` - 28 edges
2. `QueryIntent` - 20 edges
3. `GeminiClient` - 14 edges
4. `LLMQuotaError` - 13 edges
5. `OpenRouterClient` - 13 edges
6. `run_find_dish()` - 12 edges
7. `free_text()` - 12 edges
8. `LLMError` - 12 edges
9. `run_with_retries()` - 12 edges
10. `_make_user_with_recipe()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `Zero-Hallucination Principle` --rationale_for--> `LLM-Authored Text Must Be HTML-Escaped`  [INFERRED]
  README.md → .coderabbit.yaml
- `Recipe DB Backup (cp data/bot.db)` --semantically_similar_to--> `Database Reset From Scratch Procedure`  [INFERRED] [semantically similar]
  NEXT_STEPS.md → README.md
- `OPENROUTER_MODEL configured in .env, never in code` --conceptually_related_to--> `.env Key Table (BOT_TOKEN, OPENROUTER_API_KEY, GEMINI_API_KEY, OPENROUTER_MODEL, ALLOWED_USER_IDS)`  [INFERRED]
  CLAUDE.md → NEXT_STEPS.md
- `Oracle Free Tier 1GB RAM Swap Memo` --conceptually_related_to--> `Oracle Server Deployment (ubuntu@oracle)`  [INFERRED]
  README.md → NEXT_STEPS.md
- `test_parse_qty_variants()` --calls--> `parse_qty()`  [EXTRACTED]
  tests/test_shopping_list.py → bot/services/shopping_list.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **LLM provider abstraction: base + OpenRouter primary + Gemini fallback + shared retry** — readme_llm_abstraction, readme_openrouter_provider, readme_gemini_provider, readme_retry_classification [EXTRACTED 1.00]
- **Docker compose operational footguns on the Oracle host** — next_steps_build_flag_rule, next_steps_up_d_not_restart, next_steps_foreign_containers, next_steps_alembic_logger_bug [INFERRED 0.85]
- **Recipe ingestion-to-shopping-list flow constrained by zero-hallucination** — readme_recipe_recognition, readme_sqlite_storage, readme_menu_planner, readme_shopping_list, readme_zero_hallucination_principle [INFERRED 0.85]
- **Layer Boundary Rules Enforced Across Config, Docs And Tests** — coderabbit_models_data_only_rule, coderabbit_repo_sole_query_site_rule, coderabbit_thin_handlers_rule, coderabbit_services_tenancy_explicit_rule, claude_layer_rules_enforced_by_tests [INFERRED 0.85]
- **Group Tenancy Isolation Concerns** — readme_group_shared_recipe_base, report_2026_07_14_09_01_cross_group_serve_history, report_2026_07_14_09_01_fsm_group_binding, report_2026_07_14_09_01_group_scoping_invariant, coderabbit_services_tenancy_explicit_rule [INFERRED 0.85]
- **Layered Architecture Rule Set** — architecture_layer_rules, architecture_models_data_only, architecture_repo_single_sql_point, architecture_services_no_telegram, architecture_thin_handlers, architecture_new_feature_new_service [EXTRACTED 1.00]

## Communities (38 total, 15 thin omitted)

### Community 0 - "LLM Contract & Schemas"
Cohesion: 0.07
Nodes (31): Any, async_sessionmaker, BaseMiddleware, BaseSettings, get_settings(), Відкритий доступ — лише за явним ALLOWED_USER_IDS=* (dev-режим)., Settings, get_session_factory() (+23 more)

### Community 1 - "Architecture Rules & Guidelines"
Cohesion: 0.13
Nodes (26): ABC, BaseModel, Recipe, ExtractedIngredient, LLMClient, MenuPlanResult, MenuSlot, QueryIntent (+18 more)

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
Cohesion: 0.10
Nodes (28): services/ingestion.py adapter (sanctioned aiogram exception), Layer Rules (handlers → services → repo → models), Rule 1: Models are data-only, Rule 6: New feature = new service, Rule 2: repo.py is the single SQL point, Rule 3: Services know nothing about Telegram, Architecture Test Suite (tests/test_architecture.py), Rule 4: Thin handlers (no SQL, no business rules, no prompts) (+20 more)

### Community 6 - "Recipe Adding Handlers"
Cohesion: 0.13
Nodes (16): _file_part(), OpenRouterClient, LLM-клієнт через OpenRouter (OpenAI-сумісний API).  Використовується, коли задан, _text_part(), LLMClient, MenuPlanResult, QueryIntent, RecipeExtraction (+8 more)

### Community 7 - "Config, Session & Migrations"
Cohesion: 0.09
Nodes (27): Definition of Done, Goal-Driven Execution, Knowledge Graph Freshness Rule, Layer Rules (ARCHITECTURE.md), Simplicity First, Surgical Changes, tg-bot-sho-poisty (project), CodeRabbit Review Configuration (+19 more)

### Community 8 - "LLM Errors & Retry"
Cohesion: 0.16
Nodes (22): LLMError, LLMQuotaError, Exception, Перевищено ліміт запитів провайдера (HTTP 429)., Exception, T, Спільні ретраї для LLM-провайдерів з класифікацією за HTTP-статусом., Пауза перед наступною спробою; None = помилка постійна, не ретраїмо. (+14 more)

### Community 9 - "Architecture Test Internals"
Cohesion: 0.21
Nodes (22): add_hint(), AddStates, amend_apply(), amend_start(), cancel(), handle_media(), AsyncSession, Bot (+14 more)

### Community 10 - "OpenRouter Client"
Cohesion: 0.16
Nodes (16): Base, Group, GroupMember, RecipeCategory, RecipeMedia, ServeHistory, User, utcnow() (+8 more)

### Community 11 - "Menu Planning Handlers"
Cohesion: 0.19
Nodes (18): AsyncFunctionDef, FunctionDef, Module, Path, _imported_modules(), _imported_names_from(), _is_property(), _is_trivial_property() (+10 more)

### Community 12 - "Shopping List Aggregation"
Cohesion: 0.22
Nodes (17): menu_hint(), _plan_for_active_group(), AsyncSession, CallbackQuery, FSMContext, Message, User, run_menu_flow() (+9 more)

### Community 13 - "Deployment & Secrets"
Cohesion: 0.25
Nodes (12): aggregate(), _format_amount(), parse_qty(), Агрегація інгредієнтів у список покупок., «1,5» → 1.5; «1/2» → 0.5; «2-3» → 3 (беремо більше, щоб точно вистачило)., Сумує кількості за (назва, одиниця). Повертає готові рядки списку покупок., test_aggregate_decimal_comma_output(), test_aggregate_keeps_different_units_separate() (+4 more)

### Community 14 - "Recipe Rendering"
Cohesion: 0.36
Nodes (7): collect_input(), _download(), Bot, Message, Перетворення повідомлення Telegram на вхід для екстракції рецепта., Витягує текст і файли з повідомлення (фото/скрін/PDF/текст/форвард)., RecipeInput

## Knowledge Gaps
- **3 isolated node(s):** `bot service`, `./data Volume Mount`, `tg-bot-sho-poisty`
  These have ≤1 connection - possible missing edges or undocumented components.
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `OpenRouterClient` connect `Recipe Adding Handlers` to `LLM Contract & Schemas`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `LLMClient` connect `Architecture Rules & Guidelines` to `LLM Contract & Schemas`, `Architecture Test Internals`, `Dish Query Handlers`, `Shopping List Aggregation`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `LLMClient` (e.g. with `AddStates` and `GeminiClient`) actually correct?**
  _`LLMClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `GeminiClient` (e.g. with `LLMClient` and `MenuPlanResult`) actually correct?**
  _`GeminiClient` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `LLMQuotaError` (e.g. with `AddStates` and `FakeAPIError`) actually correct?**
  _`LLMQuotaError` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `bot service`, `./data Volume Mount`, `tg-bot-sho-poisty` to the rest of the system?**
  _3 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `LLM Contract & Schemas` be split into smaller, more focused modules?**
  _Cohesion score 0.0707070707070707 - nodes in this community are weakly interconnected._