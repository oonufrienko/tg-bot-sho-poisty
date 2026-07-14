# Graph Report - .  (2026-07-14)

## Corpus Check
- 14 files · ~10,134 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 309 nodes · 675 edges · 21 communities (19 shown, 2 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 29 edges (avg confidence: 0.68)
- Token cost: 52,378 input · 4,000 output

## Community Hubs (Navigation)
- LLM Interface & Schemas
- Architecture Rules & Docs
- Group Management & User
- Recipe Ingestion Flow
- Data Repository (SQL)
- Config & Middleware
- DB Models & Migrations
- Menu Planning Handlers
- Dish Query Handlers
- Architecture Test Suite
- Shopping List & Tests
- Bot Type Ref
- Project Package

## God Nodes (most connected - your core abstractions)
1. `LLMClient` - 19 edges
2. `User` - 15 edges
3. `QueryIntent` - 13 edges
4. `GeminiClient` - 13 edges
5. `Recipe` - 11 edges
6. `run_replace_flow()` - 11 edges
7. `Base` - 10 edges
8. `show_confirmation()` - 10 edges
9. `aggregate()` - 10 edges
10. `get_settings()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `BotFather (BOT_TOKEN source)` --semantically_similar_to--> `BotFather`  [INFERRED] [semantically similar]
  README.md → NEXT_STEPS.md
- `userinfobot (Telegram id lookup)` --semantically_similar_to--> `userinfobot`  [INFERRED] [semantically similar]
  README.md → NEXT_STEPS.md
- `Oracle Free Tier Server (1 GB RAM, swap memo)` --semantically_similar_to--> `Oracle Server (ssh ubuntu@oracle, ~/tg-bot-sho-poisty)`  [INFERRED] [semantically similar]
  README.md → NEXT_STEPS.md
- `bot service` --references--> `.env File on Server`  [INFERRED]
  docker-compose.yml → NEXT_STEPS.md
- `GEMINI_API_KEY` --references--> `Gemini AI`  [INFERRED]
  NEXT_STEPS.md → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Layered Architecture Rule Set** — architecture_layer_rules, architecture_models_data_only, architecture_repo_single_sql_point, architecture_services_no_telegram, architecture_thin_handlers, architecture_new_feature_new_service [EXTRACTED 1.00]
- **Server .env Configuration Bundle** — next_steps_env_file, next_steps_bot_token, next_steps_gemini_api_key, next_steps_allowed_user_ids [EXTRACTED 1.00]
- **Zero Hallucination Pipeline (LLM extracts/selects, DB renders)** — readme_zero_hallucination_principle, readme_gemini_ai, readme_llm_abstraction, readme_sqlite_db [INFERRED 0.85]

## Communities (21 total, 2 thin omitted)

### Community 0 - "LLM Interface & Schemas"
Cohesion: 0.12
Nodes (28): ABC, BaseModel, Recipe, ExtractedIngredient, LLMClient, LLMError, MenuPlanResult, MenuSlot (+20 more)

### Community 1 - "Architecture Rules & Docs"
Cohesion: 0.08
Nodes (35): services/ingestion.py adapter (sanctioned aiogram exception), Layer Rules (handlers → services → repo → models), Rule 1: Models are data-only, Rule 6: New feature = new service, Rule 2: repo.py is the single SQL point, Rule 3: Services know nothing about Telegram, Architecture Test Suite (tests/test_architecture.py), Rule 4: Thin handlers (no SQL, no business rules, no prompts) (+27 more)

### Community 2 - "Group Management & User"
Cohesion: 0.13
Nodes (32): User, create_group_finish(), create_group_start(), group_menu(), _group_overview(), GroupStates, invite_link(), members_list() (+24 more)

### Community 3 - "Recipe Ingestion Flow"
Cohesion: 0.13
Nodes (31): add_hint(), AddStates, amend_apply(), amend_start(), cancel(), handle_media(), AsyncSession, Bot (+23 more)

### Community 4 - "Data Repository (SQL)"
Cohesion: 0.17
Nodes (25): add_recipe(), create_group(), ensure_user(), get_group(), get_recipe(), get_user(), group_members(), group_recipes() (+17 more)

### Community 5 - "Config & Middleware"
Cohesion: 0.13
Nodes (16): Any, async_sessionmaker, BaseMiddleware, BaseSettings, Bot, get_settings(), Відкритий доступ — лише за явним ALLOWED_USER_IDS=* (dev-режим)., Settings (+8 more)

### Community 6 - "DB Models & Migrations"
Cohesion: 0.14
Nodes (16): Base, Group, GroupMember, RecipeCategory, RecipeMedia, ServeHistory, utcnow(), datetime (+8 more)

### Community 7 - "Menu Planning Handlers"
Cohesion: 0.21
Nodes (20): menu_hint(), _plan_for_active_group(), AsyncSession, CallbackQuery, FSMContext, LLMClient, Message, QueryIntent (+12 more)

### Community 8 - "Dish Query Handlers"
Cohesion: 0.26
Nodes (19): another_dish(), ask_hint(), choose_dish(), free_text(), _meal_type(), AsyncSession, CallbackQuery, FSMContext (+11 more)

### Community 9 - "Architecture Test Suite"
Cohesion: 0.19
Nodes (18): AsyncFunctionDef, FunctionDef, Module, Path, _imported_modules(), _imported_names_from(), _is_property(), _is_trivial_property() (+10 more)

### Community 10 - "Shopping List & Tests"
Cohesion: 0.25
Nodes (12): aggregate(), _format_amount(), parse_qty(), Агрегація інгредієнтів у список покупок., «1,5» → 1.5; «1/2» → 0.5; «2-3» → 3 (беремо більше, щоб точно вистачило)., Сумує кількості за (назва, одиниця). Повертає готові рядки списку покупок., test_aggregate_decimal_comma_output(), test_aggregate_keeps_different_units_separate() (+4 more)

## Knowledge Gaps
- **6 isolated node(s):** `tg-bot-sho-poisty`, `./data Volume Mount`, `aiogram 3 Long Polling`, `BotFather (BOT_TOKEN source)`, `userinfobot (Telegram id lookup)` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `run_migrations()` connect `Config & Middleware` to `Architecture Test Suite`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `Config & Middleware` to `DB Models & Migrations`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `LLMClient` (e.g. with `AddStates` and `GeminiClient`) actually correct?**
  _`LLMClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `User` (e.g. with `AddStates` and `GroupStates`) actually correct?**
  _`User` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `GeminiClient` (e.g. with `LLMClient` and `LLMError`) actually correct?**
  _`GeminiClient` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `tg-bot-sho-poisty`, `./data Volume Mount`, `aiogram 3 Long Polling` to the rest of the system?**
  _6 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `LLM Interface & Schemas` be split into smaller, more focused modules?**
  _Cohesion score 0.11522198731501057 - nodes in this community are weakly interconnected._