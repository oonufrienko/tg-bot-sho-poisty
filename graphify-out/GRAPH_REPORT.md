# Graph Report - .  (2026-07-13)

## Corpus Check
- Corpus is ~8,724 words - fits in a single context window. You may not need a graph.

## Summary
- 259 nodes · 653 edges · 19 communities (18 shown, 1 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 30 edges (avg confidence: 0.69)
- Token cost: 33,603 input · 2,900 output

## Community Hubs (Navigation)
- LLM Interface & Schemas
- Database Models & Repository
- Recipe Ingestion Flow
- Dish Query Handlers
- Config & Migration Setup
- Group Management
- Menu Planning & Rendering
- Product Docs & Onboarding
- Shopping List & Tests
- Deployment & Infrastructure
- Project Package

## God Nodes (most connected - your core abstractions)
1. `User` - 32 edges
2. `LLMClient` - 26 edges
3. `Recipe` - 20 edges
4. `QueryIntent` - 19 edges
5. `GeminiClient` - 15 edges
6. `send_long()` - 14 edges
7. `free_text()` - 13 edges
8. `run_menu_flow()` - 12 edges
9. `run_replace_flow()` - 12 edges
10. `Base` - 11 edges

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
- **Environment Configuration (.env values)** — next_steps_bot_token, next_steps_gemini_api_key, next_steps_allowed_user_ids, next_steps_env_file [EXTRACTED 1.00]
- **Zero-Hallucination Recipe Pipeline** — readme_gemini_ai, readme_recipe_recognition, readme_sqlite_db, readme_zero_hallucination_principle [EXTRACTED 1.00]

## Communities (19 total, 1 thin omitted)

### Community 0 - "LLM Interface & Schemas"
Cohesion: 0.12
Nodes (28): ABC, BaseModel, Recipe, ExtractedIngredient, LLMClient, LLMError, MenuPlanResult, MenuSlot (+20 more)

### Community 1 - "Database Models & Repository"
Cohesion: 0.12
Nodes (34): Base, Group, GroupMember, RecipeCategory, RecipeMedia, ServeHistory, utcnow(), add_recipe() (+26 more)

### Community 2 - "Recipe Ingestion Flow"
Cohesion: 0.16
Nodes (27): add_hint(), AddStates, amend_apply(), amend_start(), cancel(), handle_media(), AsyncSession, Bot (+19 more)

### Community 3 - "Dish Query Handlers"
Cohesion: 0.21
Nodes (24): another_dish(), ask_hint(), choose_dish(), free_text(), _meal_type(), AsyncSession, Bot, CallbackQuery (+16 more)

### Community 4 - "Config & Migration Setup"
Cohesion: 0.14
Nodes (14): Any, async_sessionmaker, BaseMiddleware, BaseSettings, get_settings(), Settings, get_session_factory(), AsyncSession (+6 more)

### Community 5 - "Group Management"
Cohesion: 0.18
Nodes (23): User, create_group_finish(), create_group_start(), group_menu(), _group_overview(), GroupStates, invite_link(), members_list() (+15 more)

### Community 6 - "Menu Planning & Rendering"
Cohesion: 0.18
Nodes (19): menu_hint(), AsyncSession, CallbackQuery, FSMContext, Message, run_menu_flow(), run_replace_flow(), send_shopping_list() (+11 more)

### Community 7 - "Product Docs & Onboarding"
Cohesion: 0.12
Nodes (17): ALLOWED_USER_IDS Whitelist Variable, BOT_TOKEN, BotFather, GEMINI_API_KEY, userinfobot, aiogram 3 Long Polling Handlers, BotFather, Gemini AI (+9 more)

### Community 8 - "Shopping List & Tests"
Cohesion: 0.25
Nodes (12): aggregate(), _format_amount(), parse_qty(), Агрегація інгредієнтів у список покупок., «1,5» → 1.5; «1/2» → 0.5; «2-3» → 3 (беремо більше, щоб точно вистачило)., Сумує кількості за (назва, одиниця). Повертає готові рядки списку покупок., test_aggregate_decimal_comma_output(), test_aggregate_keeps_different_units_separate() (+4 more)

### Community 9 - "Deployment & Infrastructure"
Cohesion: 0.33
Nodes (7): bot service, ./data Volume Mount, Deployment Next Steps Checklist, .env Configuration File, Oracle Server (ubuntu@oracle), Oracle Free Tier 1GB RAM Server, SQLite Database (data/bot.db)

## Knowledge Gaps
- **7 isolated node(s):** `tg-bot-sho-poisty`, `Aggregated Shopping List`, `SQLite Database (data/bot.db)`, `aiogram 3 Long Polling Handlers`, `Oracle Free Tier 1GB RAM Server` (+2 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `Group Management` to `Database Models & Repository`, `Recipe Ingestion Flow`, `Dish Query Handlers`, `Menu Planning & Rendering`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Why does `LLMClient` connect `LLM Interface & Schemas` to `Recipe Ingestion Flow`, `Dish Query Handlers`, `Menu Planning & Rendering`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `User` (e.g. with `AddStates` and `GroupStates`) actually correct?**
  _`User` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `LLMClient` (e.g. with `AddStates` and `GeminiClient`) actually correct?**
  _`LLMClient` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `tg-bot-sho-poisty`, `Aggregated Shopping List`, `SQLite Database (data/bot.db)` to the rest of the system?**
  _7 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `LLM Interface & Schemas` be split into smaller, more focused modules?**
  _Cohesion score 0.11522198731501057 - nodes in this community are weakly interconnected._
- **Should `Database Models & Repository` be split into smaller, more focused modules?**
  _Cohesion score 0.11875843454790823 - nodes in this community are weakly interconnected._