# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Definition of Done

**A change is finished when everything that describes it agrees with it — not when the code works.**

Before every commit, reconcile each of these with the change:

- **Docs.** [ARCHITECTURE.md](ARCHITECTURE.md) for layer or boundary changes, [README.md](README.md) for setup, commands, and env vars, this file for workflow rules.
- **Knowledge graph.** Re-run `/graphify` so `graphify-out/` reflects the new structure. A stale graph is worse than no graph: it answers questions confidently and wrongly.
- **Tests.** New behavior gets a test; changed behavior gets its existing test updated, not deleted. `uv run pytest` green.
- **User-facing instructions.** The `HELP` text in [bot/handlers/start.py](bot/handlers/start.py), button labels, and hint messages. If a user can read it, it's an interface and it can go stale.

Scope still applies (§3): reconcile what the change touched, nothing else. An unrelated docs edit is the same noise as an unrelated code edit.

The test: read the diff, the docs, and the help text together — do they contradict each other anywhere?

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

# tg-bot-sho-poisty

A family-friendly Telegram bot with a recipe database (Python 3.12, aiogram 3, SQLite). LLM via OpenRouter (`OPENROUTER_API_KEY`, model `google/gemini-3.5-flash`), falling back to the Gemini API (`GEMINI_API_KEY`) when OpenRouter is unset.

- **You must follow the layer rules from [ARCHITECTURE.md](ARCHITECTURE.md).**
  These are verified by the tests in `tests/test_architecture.py` — the tests must
  remain green; if they fail, fix the code, not the test.
- Tests: `uv run pytest`. Run: `uv run python -m bot.main` (requires `.env`).
- Deployment: server `ssh ubuntu@oracle`, directory `~/tg-bot-sho-poisty`, `docker compose up -d --build`.
