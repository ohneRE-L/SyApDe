"""
PostgreSQL-реализация CategoryRepository.
"""

from __future__ import annotations

from typing import List, Optional

import asyncpg

from internal.domain.errors import ConflictError, NotFoundError
from internal.domain.models import Category
from internal.repository.category_repository import CategoryRepository
from internal.repository.postgres.error_mapper import map_asyncpg_error


def _row_to_category(row: asyncpg.Record) -> Category:
    return Category(
        id=str(row["id"]),
        title=row["title"],
        description=row["description"],
        is_active=row["is_active"],
        created_at=row["created_at"],
    )


class PgCategoryRepository(CategoryRepository):
    """Репозиторий категорий на основе asyncpg."""

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Category]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, title, description, is_active, created_at "
                "FROM categories ORDER BY title ASC, id ASC LIMIT $1 OFFSET $2",
                limit,
                offset,
            )
        return [_row_to_category(r) for r in rows]

    async def find_by_id(self, category_id: str) -> Optional[Category]:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, title, description, is_active, created_at "
                "FROM categories WHERE id = $1",
                category_id,
            )
        return _row_to_category(row) if row else None

    async def create(self, title: str, description: Optional[str] = None) -> Category:
        try:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    INSERT INTO categories (title, description)
                    VALUES ($1, $2)
                    RETURNING id, title, description, is_active, created_at
                    """,
                    title,
                    description,
                )
        except asyncpg.PostgresError as exc:
            raise map_asyncpg_error("Category", exc) from exc
        return _row_to_category(row)

    async def update(self, category: Category) -> Category:
        try:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    UPDATE categories
                    SET title = $1, description = $2, is_active = $3
                    WHERE id = $4
                    RETURNING id, title, description, is_active, created_at
                    """,
                    category.title,
                    category.description,
                    category.is_active,
                    category.id,
                )
        except asyncpg.PostgresError as exc:
            raise map_asyncpg_error("Category", exc) from exc
        if row is None:
            raise NotFoundError("Category", category.id)
        return _row_to_category(row)

    async def delete(self, category_id: str) -> None:
        try:
            async with self._pool.acquire() as conn:
                result = await conn.execute(
                    "DELETE FROM categories WHERE id = $1",
                    category_id,
                )
        except asyncpg.ForeignKeyViolationError as exc:
            raise ConflictError("Category is referenced by existing tickets") from exc
        except asyncpg.PostgresError as exc:
            raise map_asyncpg_error("Category", exc) from exc
        if result == "DELETE 0":
            raise NotFoundError("Category", category_id)
