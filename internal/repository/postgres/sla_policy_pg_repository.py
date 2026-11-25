"""
PostgreSQL-реализация SlaPolicyRepository.
"""

from __future__ import annotations

from typing import Optional

import asyncpg

from internal.domain.models import SlaPolicy
from internal.repository.sla_policy_repository import SlaPolicyRepository


class PgSlaPolicyRepository(SlaPolicyRepository):
    """Репозиторий регламентов SLA на основе asyncpg."""

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def find_by_priority(self, priority: str) -> Optional[SlaPolicy]:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, priority, max_first_response_time_minutes,
                       max_resolution_time_minutes, created_at
                FROM sla_policies
                WHERE priority = $1
                """,
                priority,
            )
        if not row:
            return None
        return SlaPolicy(
            id=str(row["id"]),
            priority=row["priority"],
            max_first_response_time_minutes=row["max_first_response_time_minutes"],
            max_resolution_time_minutes=row["max_resolution_time_minutes"],
            created_at=row["created_at"],
        )
