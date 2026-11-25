"""
Модульные тесты TicketService (без БД и веб-сервера).

Используются заглушки (fake) репозиториев и фиксированный источник времени clock.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import uuid

import pytest

from internal.domain.errors import ConflictError, InvalidInputError, NotFoundError
from internal.domain.models import Category, SlaPolicy, Ticket, User
from internal.repository.category_repository import CategoryRepository
from internal.repository.sla_policy_repository import SlaPolicyRepository
from internal.repository.ticket_repository import TicketRepository
from internal.repository.user_repository import UserRepository
from internal.service.ticket_service import TicketService

FIXED_NOW = datetime(2026, 11, 25, 12, 0, 0, tzinfo=timezone.utc)


class FakeTicketRepo(TicketRepository):
    def __init__(self) -> None:
        self.items: Dict[str, Ticket] = {}

    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Ticket]:
        return list(self.items.values())[offset : offset + limit]

    async def find_by_id(self, ticket_id: str) -> Optional[Ticket]:
        return self.items.get(ticket_id)

    async def find_by_requester(self, requester_id: str) -> List[Ticket]:
        return [t for t in self.items.values() if t.requester_id == requester_id]

    async def create(
        self,
        subject: str,
        description: str,
        priority: str,
        category_id: str,
        requester_id: str,
        sla_policy_id: str,
        response_due_at: datetime,
        resolution_due_at: datetime,
    ) -> Ticket:
        t = Ticket(
            id=str(uuid.uuid4()),
            subject=subject,
            description=description,
            status="OPEN",
            priority=priority,
            category_id=category_id,
            requester_id=requester_id,
            sla_policy_id=sla_policy_id,
            response_due_at=response_due_at,
            resolution_due_at=resolution_due_at,
            created_at=FIXED_NOW,
            updated_at=FIXED_NOW,
        )
        self.items[t.id] = t
        return t

    async def update_status(
        self, ticket_id: str, status: str, resolved_at: Optional[datetime] = None
    ) -> Ticket:
        t = self.items.get(ticket_id)
        if t is None:
            raise NotFoundError("Ticket", ticket_id)
        t.status = status
        if resolved_at is not None:
            t.resolved_at = resolved_at
        return t

    async def delete(self, ticket_id: str) -> None:
        if ticket_id not in self.items:
            raise NotFoundError("Ticket", ticket_id)
        del self.items[ticket_id]


class FakeCategoryRepo(CategoryRepository):
    def __init__(self, categories: List[Category]) -> None:
        self.items = {c.id: c for c in categories}

    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Category]:
        return list(self.items.values())

    async def find_by_id(self, category_id: str) -> Optional[Category]:
        return self.items.get(category_id)

    async def create(self, title: str, description: Optional[str] = None) -> Category:
        raise NotImplementedError

    async def update(self, category: Category) -> Category:
        raise NotImplementedError

    async def delete(self, category_id: str) -> None:
        raise NotImplementedError


class FakeUserRepo(UserRepository):
    def __init__(self, users: List[User]) -> None:
        self.items = {u.id: u for u in users}

    async def find_all(self) -> List[User]:
        return list(self.items.values())

    async def find_by_id(self, user_id: str) -> Optional[User]:
        return self.items.get(user_id)

    async def find_by_email(self, email: str) -> Optional[User]:
        return None

    async def create(self, name: str, email: str, password_hash: str, role: str = "USER") -> User:
        raise NotImplementedError

    async def update(self, user: User) -> User:
        raise NotImplementedError

    async def delete(self, user_id: str) -> None:
        raise NotImplementedError


class FakeSlaRepo(SlaPolicyRepository):
    def __init__(self) -> None:
        self.policy = SlaPolicy(
            id="sla-high-1",
            priority="HIGH",
            max_first_response_time_minutes=60,
            max_resolution_time_minutes=480,
            created_at=FIXED_NOW,
        )

    async def find_by_priority(self, priority: str) -> Optional[SlaPolicy]:
        return self.policy if priority == "HIGH" else None


def _build_service(cat_active: bool = True, user_active: bool = True) -> TicketService:
    cat = Category("cat-1", "Network", "VPN", is_active=cat_active, created_at=FIXED_NOW)
    usr = User("usr-1", "Ivan", "ivan@example.com", "secret_hash", "USER", user_active, FIXED_NOW)
    return TicketService(
        tickets=FakeTicketRepo(),
        categories=FakeCategoryRepo([cat]),
        users=FakeUserRepo([usr]),
        sla_policies=FakeSlaRepo(),
        clock=lambda: FIXED_NOW,
    )


async def test_create_ticket_success_computes_sla_from_clock():
    svc = _build_service()
    ticket = await svc.create(
        subject="Cannot connect to VPN",
        description="VPN client returns timeout error since 09:00",
        priority="HIGH",
        category_id="cat-1",
        requester_id="usr-1",
    )
    assert ticket.status == "OPEN"
    assert ticket.response_due_at == FIXED_NOW + timedelta(minutes=60)
    assert ticket.resolution_due_at == FIXED_NOW + timedelta(minutes=480)


async def test_create_ticket_rejects_short_subject():
    svc = _build_service()
    with pytest.raises(InvalidInputError):
        await svc.create(
            subject="Hi",
            description="Long enough description here",
            priority="HIGH",
            category_id="cat-1",
            requester_id="usr-1",
        )


async def test_create_ticket_rejects_archived_category():
    svc = _build_service(cat_active=False)
    with pytest.raises(ConflictError):
        await svc.create(
            subject="Cannot connect to VPN",
            description="VPN client returns timeout error",
            priority="HIGH",
            category_id="cat-1",
            requester_id="usr-1",
        )


async def test_create_ticket_rejects_missing_user():
    svc = _build_service()
    with pytest.raises(NotFoundError):
        await svc.create(
            subject="Cannot connect to VPN",
            description="VPN client returns timeout error",
            priority="HIGH",
            category_id="cat-1",
            requester_id="missing-user",
        )


async def test_close_ticket_success_and_double_close_conflict():
    svc = _build_service()
    ticket = await svc.create(
        subject="Cannot connect to VPN",
        description="VPN client returns timeout error",
        priority="HIGH",
        category_id="cat-1",
        requester_id="usr-1",
    )
    closed = await svc.close(ticket.id)
    assert closed.status == "CLOSED"
    assert closed.resolved_at == FIXED_NOW

    with pytest.raises(ConflictError):
        await svc.close(ticket.id)
