from __future__ import annotations

import secrets
from datetime import date, datetime, timezone

from sqlalchemy import JSON, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Ключі категорій зафіксовані латиницею, підписи — для інтерфейсу.
CATEGORIES: dict[str, str] = {
    "breakfast": "🍳 Сніданок",
    "lunch": "🍲 Обід",
    "dinner": "🌙 Вечеря",
    "dessert": "🍰 Десерт",
    "salad": "🥗 Салати",
    "general": "🍽 Загальна",
}

MEAL_LABELS: dict[str, str] = {
    "breakfast": "Сніданок",
    "lunch": "Обід",
    "dinner": "Вечеря",
}


def new_invite_token() -> str:
    return secrets.token_urlsafe(8)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    tg_user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(128))
    lang: Mapped[str] = mapped_column(String(8), default="uk")
    active_group_id: Mapped[int | None] = mapped_column(
        ForeignKey("groups.id", use_alter=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.tg_user_id"))
    invite_token: Mapped[str] = mapped_column(
        String(32), unique=True, default=new_invite_token
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class GroupMember(Base):
    __tablename__ = "group_members"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.tg_user_id"), primary_key=True
    )
    role: Mapped[str] = mapped_column(String(16), default="member")


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), index=True)
    added_by: Mapped[int] = mapped_column(ForeignKey("users.tg_user_id"))
    title: Mapped[str] = mapped_column(String(256))
    # list[{"name": str, "qty": str | None, "unit": str | None}]
    ingredients: Mapped[list] = mapped_column(JSON, default=list)
    steps: Mapped[str] = mapped_column(Text, default="")
    difficulty: Mapped[int | None] = mapped_column(nullable=True)
    calories: Mapped[int | None] = mapped_column(nullable=True)
    source_type: Mapped[str] = mapped_column(String(16), default="text")
    original_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    categories: Mapped[list[RecipeCategory]] = relationship(
        cascade="all, delete-orphan", lazy="selectin"
    )
    media: Mapped[list[RecipeMedia]] = relationship(
        cascade="all, delete-orphan", lazy="selectin"
    )

    @property
    def category_keys(self) -> list[str]:
        return [c.category for c in self.categories]


class RecipeCategory(Base):
    __tablename__ = "recipe_categories"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)
    category: Mapped[str] = mapped_column(String(32), primary_key=True)


class RecipeMedia(Base):
    __tablename__ = "recipe_media"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), index=True)
    tg_file_id: Mapped[str] = mapped_column(String(256))
    media_type: Mapped[str] = mapped_column(String(16), default="photo")


class ServeHistory(Base):
    __tablename__ = "serve_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), index=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.tg_user_id"))
    meal_type: Mapped[str | None] = mapped_column(String(16), nullable=True)
    served_on: Mapped[date] = mapped_column(Date)
