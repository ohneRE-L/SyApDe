"""
Интеграционные тесты PgCategoryRepository.

Запуск:
    py -m pytest tests/integration/test_category_repository.py -v
"""

import pytest
import pytest_asyncio

from internal.domain.errors import AlreadyExistsError, NotFoundError
from internal.repository.postgres.category_pg_repository import PgCategoryRepository

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def repo(pool):
    return PgCategoryRepository(pool)


@pytest_asyncio.fixture(autouse=True)
async def cleanup(pool):
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM categories WHERE title LIKE 'TEST_%'"
        )
    yield
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM categories WHERE title LIKE 'TEST_%'"
        )


async def test_create_and_find_by_id(repo):
    cat = await repo.create("TEST_Network", "Network issues")
    assert cat.id
    assert cat.title == "TEST_Network"

    fetched = await repo.find_by_id(cat.id)
    assert fetched is not None
    assert fetched.description == "Network issues"


async def test_find_by_id_not_found(repo):
    result = await repo.find_by_id("00000000-0000-0000-0000-000000000000")
    assert result is None


async def test_find_all_includes_created(repo):
    await repo.create("TEST_Hardware")
    cats = await repo.find_all()
    titles = [c.title for c in cats]
    assert "TEST_Hardware" in titles


async def test_create_duplicate_raises(repo):
    await repo.create("TEST_Software")
    with pytest.raises(AlreadyExistsError):
        await repo.create("TEST_Software")


async def test_delete(repo):
    cat = await repo.create("TEST_Delete_Me")
    await repo.delete(cat.id)
    assert await repo.find_by_id(cat.id) is None


async def test_delete_not_found(repo):
    with pytest.raises(NotFoundError):
        await repo.delete("00000000-0000-0000-0000-000000000003")
