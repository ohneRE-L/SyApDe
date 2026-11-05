"""
Интеграционные тесты PgUserRepository.

Запуск (после docker-compose up -d db migrate):
    py -m pytest tests/integration/test_user_repository.py -v
"""

import pytest
import pytest_asyncio

from internal.domain.errors import AlreadyExistsError, NotFoundError
from internal.repository.postgres.user_pg_repository import PgUserRepository

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def repo(pool):
    return PgUserRepository(pool)


@pytest_asyncio.fixture(autouse=True)
async def cleanup(pool):
    """Удаляем тестовых пользователей до и после каждого теста."""
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM users WHERE email LIKE 'test_%@example.com'"
        )
    yield
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM users WHERE email LIKE 'test_%@example.com'"
        )


async def test_create_and_find_by_id(repo):
    user = await repo.create(
        name="Alice",
        email="test_alice@example.com",
        password_hash="hash_alice",
    )
    assert user.id
    assert user.email == "test_alice@example.com"
    assert user.role == "USER"

    fetched = await repo.find_by_id(user.id)
    assert fetched is not None
    assert fetched.name == "Alice"


async def test_find_by_id_not_found(repo):
    result = await repo.find_by_id("00000000-0000-0000-0000-000000000000")
    assert result is None


async def test_find_by_email(repo):
    await repo.create(
        name="Bob",
        email="test_bob@example.com",
        password_hash="hash_bob",
        role="SUPPORT_AGENT",
    )
    user = await repo.find_by_email("test_bob@example.com")
    assert user is not None
    assert user.role == "SUPPORT_AGENT"


async def test_find_all_includes_created(repo):
    await repo.create("Carol", "test_carol@example.com", "hash_carol")
    users = await repo.find_all()
    emails = [u.email for u in users]
    assert "test_carol@example.com" in emails


async def test_create_duplicate_email_raises(repo):
    await repo.create("Dave", "test_dave@example.com", "hash_dave")
    with pytest.raises(AlreadyExistsError):
        await repo.create("Dave2", "test_dave@example.com", "hash_dave2")


async def test_update(repo):
    user = await repo.create("Eve", "test_eve@example.com", "hash_eve")
    user.name = "Eve Updated"
    updated = await repo.update(user)
    assert updated.name == "Eve Updated"


async def test_update_not_found(repo):
    from internal.domain.models import User
    from datetime import datetime, timezone

    ghost = User(
        id="00000000-0000-0000-0000-000000000001",
        name="Ghost",
        email="test_ghost@example.com",
        password_hash="x",
        role="USER",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    with pytest.raises(NotFoundError):
        await repo.update(ghost)


async def test_delete(repo):
    user = await repo.create("Frank", "test_frank@example.com", "hash_frank")
    await repo.delete(user.id)
    assert await repo.find_by_id(user.id) is None


async def test_delete_not_found(repo):
    with pytest.raises(NotFoundError):
        await repo.delete("00000000-0000-0000-0000-000000000002")
