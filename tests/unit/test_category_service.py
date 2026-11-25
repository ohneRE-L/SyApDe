"""
Модульные тесты CategoryService (без БД и веб-сервера, на in-memory заглушке).
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
import uuid

import pytest

from internal.domain.errors import AlreadyExistsError, InvalidInputError, NotFoundError
from internal.domain.models import Category
from internal.repository.category_repository import CategoryRepository
from internal.service.category_service import CategoryService


class FakeCategoryRepository(CategoryRepository):
    def __init__(self) -> None:
        self.items: Dict[str, Category] = {}

    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Category]:
        vals = sorted(self.items.values(), key=lambda c: c.title)
        return vals[offset : offset + limit]

    async def find_by_id(self, category_id: str) -> Optional[Category]:
        return self.items.get(category_id)

    async def create(self, title: str, description: Optional[str] = None) -> Category:
        if any(c.title == title for c in self.items.values()):
            raise AlreadyExistsError("Category", "title", title)
        cat = Category(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        self.items[cat.id] = cat
        return cat

    async def update(self, category: Category) -> Category:
        if category.id not in self.items:
            raise NotFoundError("Category", category.id)
        self.items[category.id] = category
        return category

    async def delete(self, category_id: str) -> None:
        if category_id not in self.items:
            raise NotFoundError("Category", category_id)
        del self.items[category_id]


async def test_category_crud_lifecycle():
    svc = CategoryService(FakeCategoryRepository())
    created = await svc.create("  Network  ", "  VPN & Wi-Fi  ")
    assert created.title == "Network"
    assert created.description == "VPN & Wi-Fi"

    fetched = await svc.get(created.id)
    assert fetched.id == created.id

    updated = await svc.update(created.id, "Network & VPN", "Updated", is_active=False)
    assert updated.is_active is False

    await svc.delete(created.id)
    with pytest.raises(NotFoundError):
        await svc.get(created.id)


async def test_create_empty_title_raises_invalid_input():
    svc = CategoryService(FakeCategoryRepository())
    with pytest.raises(InvalidInputError):
        await svc.create("   ")
