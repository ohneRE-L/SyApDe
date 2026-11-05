"""
Интеграционные тесты PgTicketRepository.

Перед запуском в БД должны существовать вспомогательные записи:
  user, category, sla_policy — создаются фикстурами ниже.

Запуск:
    py -m pytest tests/integration/test_ticket_repository.py -v
"""

from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio

from internal.domain.errors import NotFoundError
from internal.repository.postgres.category_pg_repository import PgCategoryRepository
from internal.repository.postgres.ticket_pg_repository import PgTicketRepository
from internal.repository.postgres.user_pg_repository import PgUserRepository

pytestmark = pytest.mark.asyncio

_NOW = datetime.now(timezone.utc)
_RESP_DUE = _NOW + timedelta(hours=4)
_RESOL_DUE = _NOW + timedelta(hours=24)


@pytest_asyncio.fixture
async def user(pool):
    repo = PgUserRepository(pool)
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = 'ticket_test@example.com'")
    u = await repo.create("TicketUser", "ticket_test@example.com", "hash_x")
    yield u
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE id = $1", u.id)


@pytest_asyncio.fixture
async def category(pool):
    repo = PgCategoryRepository(pool)
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM categories WHERE title = 'TEST_TicketCat'")
    cat = await repo.create("TEST_TicketCat", "For ticket tests")
    yield cat
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM categories WHERE id = $1", cat.id)


@pytest_asyncio.fixture
async def sla_id(pool):
    """Возвращает id существующей SLA-политики (вставленной миграцией, если есть)."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT id FROM sla_policies LIMIT 1")
        if row:
            yield str(row["id"])
            return
        # Если таблица пустая — вставляем одну строку
        row = await conn.fetchrow(
            """
            INSERT INTO sla_policies
                (priority, max_first_response_time_minutes, max_resolution_time_minutes)
            VALUES ('MEDIUM', 240, 1440)
            ON CONFLICT (priority) DO UPDATE SET priority = EXCLUDED.priority
            RETURNING id
            """
        )
        sid = str(row["id"])
    yield sid


@pytest_asyncio.fixture
async def repo(pool):
    return PgTicketRepository(pool)


@pytest_asyncio.fixture(autouse=True)
async def cleanup_tickets(pool):
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM tickets WHERE subject LIKE 'TEST:%'")
    yield
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM tickets WHERE subject LIKE 'TEST:%'")


async def test_create_and_find_by_id(repo, user, category, sla_id):
    ticket = await repo.create(
        subject="TEST: cannot login",
        description="User cannot login since morning",
        priority="HIGH",
        category_id=category.id,
        requester_id=user.id,
        sla_policy_id=sla_id,
        response_due_at=_RESP_DUE,
        resolution_due_at=_RESOL_DUE,
    )
    assert ticket.id
    assert ticket.status == "OPEN"

    fetched = await repo.find_by_id(ticket.id)
    assert fetched is not None
    assert fetched.subject == "TEST: cannot login"


async def test_find_by_id_not_found(repo):
    result = await repo.find_by_id("00000000-0000-0000-0000-000000000000")
    assert result is None


async def test_find_by_requester(repo, user, category, sla_id):
    await repo.create(
        subject="TEST: printer broken",
        description="Printer on 3rd floor",
        priority="LOW",
        category_id=category.id,
        requester_id=user.id,
        sla_policy_id=sla_id,
        response_due_at=_RESP_DUE,
        resolution_due_at=_RESOL_DUE,
    )
    tickets = await repo.find_by_requester(user.id)
    assert any(t.subject == "TEST: printer broken" for t in tickets)


async def test_find_all(repo, user, category, sla_id):
    await repo.create(
        subject="TEST: find all check",
        description="desc",
        priority="MEDIUM",
        category_id=category.id,
        requester_id=user.id,
        sla_policy_id=sla_id,
        response_due_at=_RESP_DUE,
        resolution_due_at=_RESOL_DUE,
    )
    all_tickets = await repo.find_all()
    assert any(t.subject == "TEST: find all check" for t in all_tickets)


async def test_update_status(repo, user, category, sla_id):
    ticket = await repo.create(
        subject="TEST: status update",
        description="desc",
        priority="MEDIUM",
        category_id=category.id,
        requester_id=user.id,
        sla_policy_id=sla_id,
        response_due_at=_RESP_DUE,
        resolution_due_at=_RESOL_DUE,
    )
    updated = await repo.update_status(ticket.id, "IN_PROGRESS")
    assert updated.status == "IN_PROGRESS"


async def test_update_status_not_found(repo):
    with pytest.raises(NotFoundError):
        await repo.update_status("00000000-0000-0000-0000-000000000000", "RESOLVED")


async def test_delete(repo, user, category, sla_id):
    ticket = await repo.create(
        subject="TEST: delete me",
        description="desc",
        priority="LOW",
        category_id=category.id,
        requester_id=user.id,
        sla_policy_id=sla_id,
        response_due_at=_RESP_DUE,
        resolution_due_at=_RESOL_DUE,
    )
    await repo.delete(ticket.id)
    assert await repo.find_by_id(ticket.id) is None


async def test_delete_not_found(repo):
    with pytest.raises(NotFoundError):
        await repo.delete("00000000-0000-0000-0000-000000000004")
