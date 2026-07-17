"""Інтерфейс LLM і схеми structured output.

Ключовий принцип: LLM ніколи не генерує текст рецепта — лише
(1) екстрактує структуру з даних користувача і (2) обирає ID рецептів
зі списку кандидатів, який дає код. Рендер відповіді — завжди з БД.
"""

from abc import ABC, abstractmethod
from typing import Literal, Optional

from pydantic import BaseModel, Field

CategoryKey = Literal[
    "breakfast", "lunch", "dinner", "dessert", "salad", "general"
]
MealKey = Literal["breakfast", "lunch", "dinner"]


class ExtractedIngredient(BaseModel):
    name: str
    qty: Optional[str] = None  # рядок, щоб зберегти «1,5», «по смаку», «2-3»
    unit: Optional[str] = None


class RecipeExtraction(BaseModel):
    is_recipe: bool
    title: Optional[str] = None
    ingredients: list[ExtractedIngredient] = Field(default_factory=list)
    steps: Optional[str] = None
    suggested_categories: list[CategoryKey] = Field(default_factory=list)
    difficulty: Optional[int] = None  # 1 — легкий/швидкий … 4 — складний
    calories: Optional[int] = None  # лише якщо явно вказано в тексті
    language: Optional[str] = None
    # Що не вдалося розпізнати — питання користувачу, нічого не вигадуємо
    missing_info: list[str] = Field(default_factory=list)


IntentKey = Literal[
    "find_dish",
    "plan_menu",
    "add_recipe",
    "recent_dishes",
    "another_suggestion",
    "replace_slot",
    "help_or_chat",
]


class QueryIntent(BaseModel):
    intent: IntentKey
    meal_types: list[CategoryKey] = Field(default_factory=list)
    include_ingredients: list[str] = Field(default_factory=list)
    exclude_ingredients: list[str] = Field(default_factory=list)
    specific_dish: Optional[str] = None
    max_calories_per_day: Optional[int] = None
    persons: Optional[int] = None
    days: Optional[int] = None
    meals_per_day: Optional[int] = None
    max_difficulty: Optional[int] = None
    replace_day: Optional[int] = None
    replace_meal: Optional[MealKey] = None


class SelectionResult(BaseModel):
    selected_ids: list[int] = Field(default_factory=list)
    need_clarification: bool = False
    clarification_question: Optional[str] = None
    option_ids: list[int] = Field(default_factory=list)


class MenuSlot(BaseModel):
    day: int
    meal: MealKey
    recipe_id: int


class MenuPlanResult(BaseModel):
    slots: list[MenuSlot] = Field(default_factory=list)
    # Якщо рецептів не вистачає для збалансованого меню — чесно сказати про це
    comment: Optional[str] = None


class LLMError(Exception):
    pass


class LLMQuotaError(LLMError):
    """Перевищено ліміт запитів провайдера (HTTP 429)."""


class LLMClient(ABC):
    """Абстракція над провайдером — щоб згодом замінити Gemini на Claude."""

    @abstractmethod
    async def extract_recipe(
        self, text: str | None, files: list[tuple[bytes, str]]
    ) -> RecipeExtraction: ...

    @abstractmethod
    async def route_query(self, text: str) -> QueryIntent: ...

    @abstractmethod
    async def select_recipes(
        self, user_query: str, candidates: list[dict], count: int = 1
    ) -> SelectionResult: ...

    @abstractmethod
    async def plan_menu(
        self,
        user_query: str,
        candidates: list[dict],
        days: int,
        meals_per_day: int,
        max_calories_per_day: int | None,
    ) -> MenuPlanResult: ...
