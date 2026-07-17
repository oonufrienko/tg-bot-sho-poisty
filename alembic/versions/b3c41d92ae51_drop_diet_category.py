"""Прибрати категорію «Дієта».

Категорію видалено з інтерфейсу. Рецепти, в яких дієта була ЄДИНОЮ
категорією, переносяться в «Загальну», щоб не випасти з фільтрів;
у решти рядок diet просто зникає.

Revision ID: b3c41d92ae51
Revises: f82a10d770df
Create Date: 2026-07-17
"""

from typing import Sequence, Union

from alembic import op

revision: str = "b3c41d92ae51"
down_revision: Union[str, None] = "f82a10d770df"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Спершу «сироти»: дієта — єдина категорія → стає general.
    # PK (recipe_id, category) не конфліктне: у таких рецептів general немає.
    op.execute(
        """
        UPDATE recipe_categories SET category = 'general'
        WHERE category = 'diet'
          AND recipe_id NOT IN (
              SELECT recipe_id FROM recipe_categories WHERE category != 'diet'
          )
        """
    )
    # Решта diet-рядків належить рецептам з іншими категоріями — прибрати.
    op.execute("DELETE FROM recipe_categories WHERE category = 'diet'")


def downgrade() -> None:
    # Дані про те, хто був «дієтою», втрачені — відкат неможливий.
    pass
