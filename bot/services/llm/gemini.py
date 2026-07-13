import asyncio
import json
import logging

from google import genai
from google.genai import types
from pydantic import BaseModel

from bot.services.llm import prompts
from bot.services.llm.base import (
    LLMClient,
    LLMError,
    MenuPlanResult,
    QueryIntent,
    RecipeExtraction,
    SelectionResult,
)

logger = logging.getLogger(__name__)

# Безкоштовний tier інколи відповідає 429/503 — робимо кілька спроб з паузою.
RETRIES = 3
RETRY_DELAY = 5.0


class GeminiClient(LLMClient):
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self._client = genai.Client(api_key=api_key)
        self._model = model

    async def _generate[T: BaseModel](
        self, contents: list, schema: type[T], temperature: float = 0.2
    ) -> T:
        last_error: Exception | None = None
        for attempt in range(RETRIES):
            try:
                response = await self._client.aio.models.generate_content(
                    model=self._model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=schema,
                        temperature=temperature,
                    ),
                )
                if response.parsed is not None:
                    return response.parsed  # type: ignore[return-value]
                return schema.model_validate_json(response.text or "")
            except Exception as exc:  # noqa: BLE001 — ретраїмо будь-який збій API
                last_error = exc
                logger.warning("Gemini attempt %s failed: %s", attempt + 1, exc)
                if attempt < RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY * (attempt + 1))
        raise LLMError(f"Gemini не відповів після {RETRIES} спроб: {last_error}")

    async def extract_recipe(
        self, text: str | None, files: list[tuple[bytes, str]]
    ) -> RecipeExtraction:
        contents: list = [prompts.EXTRACT_RECIPE]
        if text:
            contents.append(text)
        for data, mime_type in files:
            contents.append(types.Part.from_bytes(data=data, mime_type=mime_type))
        return await self._generate(contents, RecipeExtraction)

    async def route_query(self, text: str) -> QueryIntent:
        return await self._generate(
            [prompts.ROUTE_QUERY, f"Запит користувача: {text}"], QueryIntent
        )

    async def select_recipes(
        self, user_query: str, candidates: list[dict], count: int = 1
    ) -> SelectionResult:
        prompt = prompts.SELECT_RECIPES.format(
            count=count,
            query=user_query,
            candidates=json.dumps(candidates, ensure_ascii=False),
        )
        return await self._generate([prompt], SelectionResult)

    async def plan_menu(
        self,
        user_query: str,
        candidates: list[dict],
        days: int,
        meals_per_day: int,
        max_calories_per_day: int | None,
    ) -> MenuPlanResult:
        calories_rule = (
            prompts.CALORIES_RULE.format(max_calories=max_calories_per_day)
            if max_calories_per_day
            else prompts.NO_CALORIES_RULE
        )
        prompt = prompts.PLAN_MENU.format(
            days=days,
            meals_per_day=meals_per_day,
            calories_rule=calories_rule,
            query=user_query,
            candidates=json.dumps(candidates, ensure_ascii=False),
        )
        return await self._generate([prompt], MenuPlanResult, temperature=0.5)
