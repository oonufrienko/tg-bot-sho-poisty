"""LLM-клієнт через OpenRouter (OpenAI-сумісний API).

Використовується, коли задано OPENROUTER_API_KEY — платний доступ до Gemini
без лімітів безкоштовного тарифу AI Studio.
"""

import base64
import json

from openai import AsyncOpenAI
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
from bot.services.llm.retry import run_with_retries

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
# Gemini читає PDF нативно; без engine=native OpenRouter вмикає платний mistral-ocr
PDF_PLUGINS = [{"id": "file-parser", "pdf": {"engine": "native"}}]


def _text_part(text: str) -> dict:
    return {"type": "text", "text": text}


def _file_part(data: bytes, mime_type: str) -> dict:
    encoded = base64.b64encode(data).decode()
    if mime_type == "application/pdf":
        return {
            "type": "file",
            "file": {
                "filename": "recipe.pdf",
                "file_data": f"data:application/pdf;base64,{encoded}",
            },
        }
    return {
        "type": "image_url",
        "image_url": {"url": f"data:{mime_type};base64,{encoded}"},
    }


class OpenRouterClient(LLMClient):
    def __init__(self, api_key: str, model: str = "google/gemini-3.1-flash-lite-preview"):
        self._client = AsyncOpenAI(api_key=api_key, base_url=OPENROUTER_BASE_URL)
        self._model = model

    async def _generate[T: BaseModel](
        self, parts: list[dict], schema: type[T], temperature: float = 0.2
    ) -> T:
        # require_parameters — роутити лише до провайдерів зі structured output
        extra_body: dict = {"provider": {"require_parameters": True}}
        if any(part.get("type") == "file" for part in parts):
            extra_body["plugins"] = PDF_PLUGINS

        async def attempt() -> T:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": parts}],
                temperature=temperature,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": schema.__name__,
                        "strict": True,
                        "schema": schema.model_json_schema(),
                    },
                },
                extra_body=extra_body,
            )
            if not response.choices:
                raise LLMError(f"OpenRouter повернув порожню відповідь: {response}")
            return schema.model_validate_json(
                response.choices[0].message.content or ""
            )

        # openai.APIStatusError має атрибут .status_code з HTTP-статусом
        return await run_with_retries(
            attempt, lambda exc: getattr(exc, "status_code", None), "OpenRouter"
        )

    async def extract_recipe(
        self, text: str | None, files: list[tuple[bytes, str]]
    ) -> RecipeExtraction:
        parts = [_text_part(prompts.EXTRACT_RECIPE)]
        if text:
            parts.append(_text_part(text))
        for data, mime_type in files:
            parts.append(_file_part(data, mime_type))
        return await self._generate(parts, RecipeExtraction)

    async def route_query(self, text: str) -> QueryIntent:
        parts = [
            _text_part(prompts.ROUTE_QUERY),
            _text_part(f"Запит користувача: {text}"),
        ]
        return await self._generate(parts, QueryIntent)

    async def select_recipes(
        self, user_query: str, candidates: list[dict], count: int = 1
    ) -> SelectionResult:
        prompt = prompts.SELECT_RECIPES.format(
            count=count,
            query=user_query,
            candidates=json.dumps(candidates, ensure_ascii=False),
        )
        return await self._generate([_text_part(prompt)], SelectionResult)

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
        return await self._generate([_text_part(prompt)], MenuPlanResult, temperature=0.5)
