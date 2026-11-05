"""
PostgreSQL-реализация TicketRepository.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

import asyncpg

from internal.domain.errors import NotFoundError
from internal.domain.models import Ticket
from internal.repository.postgres.error_mapper import map_asyncpg_error
from internal.repository.ticket_repository import TicketRepository


def _row_to_ticket(row: asyncpg.Record) -> Ticket:
    return Ticket(
        id=str(row["id"]),
        subject=row["subject"],
        description=row["description"],
        status=row["status"],
        priority=row["priority"],
        category_id=str(row["category_id"]),
        requester_id=str(row["requester_id"]),
        sla_policy_id=str(row["sla_policy_id"]),
        response_due_at=row["response_due_at"],
        resolution_due_at=row["resolution_due_at"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        assignee_id=str(row["assignee_id"]) if row["assignee_id"] else None,
        first_responded_at=row["first_responded_at"],
        resolved_at=row["resolved_at"],
    )


_SELECT = (
    "SELECT id, subject, description, status, priority, "
    "category_id, requester_id, assignee_id, sla_policy_id, "
    "response_due_at, resolution_due_at, first_responded_at, "
    "resolved_at, created_at, updated_at FROM tickets"
)


class PgTicketRepository(TicketRepository):
    """Репозиторий тикетов на основе asyncpg."""

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def find_all(self) -> List[Ticket]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(f"{_SELECT} ORDER BY created_at DESC")
        return [_row_to_ticket(r) for r in rows]

    async def find_by_id(self, ticket_id: str) -> Optional[Ticket]:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(f"{_SELECT} WHERE id = $1", ticket_id)
        return _row_to_ticket(row) if row else None

    async def find_by_requester(self, requester_id: str) -> List[Ticket]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                f"{_SELECT} WHERE requester_id = $1 ORDER BY created_at DESC",
                requester_id,
            )
        return [_row_to_ticket(r) for r in rows]

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
        try:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    INSERT INTO tickets
                        (subject, description, priority,
                         category_id, requester_id, sla_policy_id,
                         response_due_at, resolution_due_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    RETURNING id, subject, description, status, priority,
                              category_id, requester_id, assignee_id, sla_policy_id,
                              response_due_at, resolution_due_at, first_responded_at,
                              resolved_at, created_at, updated_at
                    """,
                    subject,
                    description,
                    priority,
                    category_id,
                    requester_id,
                    sla_policy_id,
                    response_due_at,
                    resolution_due_at,
                )
        except asyncpg.PostgresError as exc:
            raise map_asyncpg_error("Ticket", exc) from exc
        return _row_to_ticket(row)

    async def update_status(self, ticket_id: str, status: str) -> Ticket:
        try:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    UPDATE tickets
                    SET status = $1, updated_at = now()
                    WHERE id = $2
                    RETURNING id, subject, description, status, priority,
                              category_id, requester_id, assignee_id, sla_policy_id,
                              response_due_at, resolution_due_at, first_responded_at,
                              resolved_at, created_at, updated_at
                    """,
                    status,
                    ticket_id,
                )
        except asyncpg.PostgresError as exc:
            raise map_asyncpg_error("Ticket", exc) from exc
        if row is None:
            raise NotFoundError("Ticket", ticket_id)
        return _row_to_ticket(row)

    async def delete(self, ticket_id: str) -> None:
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM tickets WHERE id = $1",
                ticket_id,
            )
        if result == "DELETE 0":
            raise NotFoundError("Ticket", ticket_id)
