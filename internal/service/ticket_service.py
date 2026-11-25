"""
Сервис управления обращениями (тикетами) с проверкой бизнес-правил.

Зависимости (репозитории и источник времени) передаются извне через конструктор.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Callable, List

from internal.domain.errors import ConflictError, InvalidInputError, NotFoundError
from internal.domain.models import Ticket
from internal.repository.category_repository import CategoryRepository
from internal.repository.sla_policy_repository import SlaPolicyRepository
from internal.repository.ticket_repository import TicketRepository
from internal.repository.user_repository import UserRepository

VALID_PRIORITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TicketService:
    """Бизнес-логика для тикетов службы поддержки."""

    def __init__(
        self,
        tickets: TicketRepository,
        categories: CategoryRepository,
        users: UserRepository,
        sla_policies: SlaPolicyRepository,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._tickets = tickets
        self._categories = categories
        self._users = users
        self._sla_policies = sla_policies
        self._clock = clock

    async def create(
        self,
        subject: str,
        description: str,
        priority: str,
        category_id: str,
        requester_id: str,
    ) -> Ticket:
        # Бизнес-правило 1 (инвариант входных данных): длина темы/описания и допустимый приоритет
        clean_subject = subject.strip()
        clean_desc = description.strip()
        if len(clean_subject) < 5 or len(clean_subject) > 255:
            raise InvalidInputError("Ticket subject must be between 5 and 255 characters")
        if len(clean_desc) < 10:
            raise InvalidInputError("Ticket description must be at least 10 characters")
        if priority not in VALID_PRIORITIES:
            raise InvalidInputError(f"Priority must be one of: {', '.join(sorted(VALID_PRIORITIES))}")

        # Бизнес-правило 2 (существование и состояние категории): категория должна существовать и быть активной
        category = await self._categories.find_by_id(category_id)
        if category is None:
            raise NotFoundError("Category", category_id)
        if not category.is_active:
            raise ConflictError(f"Category {category_id} is archived and cannot accept new tickets")

        # Бизнес-правило 3 (существование и состояние пользователя): заявитель должен существовать и быть активным
        requester = await self._users.find_by_id(requester_id)
        if requester is None:
            raise NotFoundError("User", requester_id)
        if not requester.is_active:
            raise ConflictError(f"User {requester_id} is deactivated")

        # Бизнес-правило 4 (расчёт SLA по времени): дедлайны считаются от переданного источника времени clock
        sla = await self._sla_policies.find_by_priority(priority)
        if sla is None:
            raise NotFoundError("SlaPolicy", priority)

        now = self._clock()
        response_due_at = now + timedelta(minutes=sla.max_first_response_time_minutes)
        resolution_due_at = now + timedelta(minutes=sla.max_resolution_time_minutes)

        return await self._tickets.create(
            subject=clean_subject,
            description=clean_desc,
            priority=priority,
            category_id=category_id,
            requester_id=requester_id,
            sla_policy_id=sla.id,
            response_due_at=response_due_at,
            resolution_due_at=resolution_due_at,
        )

    async def get(self, ticket_id: str) -> Ticket:
        ticket = await self._tickets.find_by_id(ticket_id)
        if ticket is None:
            raise NotFoundError("Ticket", ticket_id)
        return ticket

    async def list(self, limit: int = 20, offset: int = 0) -> List[Ticket]:
        safe_limit = max(1, min(limit, 100))
        safe_offset = max(0, offset)
        return await self._tickets.find_all(limit=safe_limit, offset=safe_offset)

    async def close(self, ticket_id: str) -> Ticket:
        ticket = await self.get(ticket_id)
        # Бизнес-правило 5 (переход состояния): нельзя повторно закрыть уже закрытый тикет
        if ticket.status == "CLOSED":
            raise ConflictError(f"Ticket {ticket_id} is already closed")
        return await self._tickets.update_status(
            ticket_id=ticket_id,
            status="CLOSED",
            resolved_at=self._clock(),
        )
