"""
Сервис управления категориями обращений (полный CRUD).
"""

from __future__ import annotations

from typing import List, Optional

from internal.domain.errors import InvalidInputError, NotFoundError
from internal.domain.models import Category
from internal.repository.category_repository import CategoryRepository


class CategoryService:
    """Бизнес-логика для категорий обращений."""

    def __init__(self, categories: CategoryRepository) -> None:
        self._categories = categories

    async def create(self, title: str, description: Optional[str] = None) -> Category:
        clean_title = title.strip()
        if not clean_title or len(clean_title) > 100:
            raise InvalidInputError("Category title must be between 1 and 100 characters")
        clean_desc = description.strip() if description is not None else None
        return await self._categories.create(clean_title, clean_desc)

    async def get(self, category_id: str) -> Category:
        category = await self._categories.find_by_id(category_id)
        if category is None:
            raise NotFoundError("Category", category_id)
        return category

    async def list(self, limit: int = 20, offset: int = 0) -> List[Category]:
        safe_limit = max(1, min(limit, 100))
        safe_offset = max(0, offset)
        return await self._categories.find_all(limit=safe_limit, offset=safe_offset)

    async def update(
        self,
        category_id: str,
        title: str,
        description: Optional[str] = None,
        is_active: bool = True,
    ) -> Category:
        clean_title = title.strip()
        if not clean_title or len(clean_title) > 100:
            raise InvalidInputError("Category title must be between 1 and 100 characters")
        existing = await self.get(category_id)
        updated = Category(
            id=existing.id,
            title=clean_title,
            description=description.strip() if description is not None else None,
            is_active=is_active,
            created_at=existing.created_at,
        )
        return await self._categories.update(updated)

    async def delete(self, category_id: str) -> None:
        await self._categories.delete(category_id)
