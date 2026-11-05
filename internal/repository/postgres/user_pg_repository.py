"""
PostgreSQL-реализация UserRepository.

Все запросы используют параметризованные плейсхолдеры ($1, $2, …),
что исключает возможность SQL-инъекций.
"""

from __future__ import annotations

from typing import List, Optional

import asyncpg

from internal.domain.errors import NotFoundError
from internal.domain.models import User
from internal.repository.postgres.error_mapper import map_asyncpg_error
from internal.repository.user_repository import UserRepository


def _row_to_user(row: asyncpg.Record) -> User:
    return User(
        id=str(row["id"]),
        name=row["name"],
        email=row["email"],
        password_hash=row["password_hash"],
        role=row["role"],
        is_active=row["is_active"],
        created_at=row["created_at"],
    )


class PgUserRepository(UserRepository):
    """Репозиторий пользователей на основе asyncpg."""

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def find_all(self) -> List[User]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, name, email, password_hash, role, is_active, created_at "
                "FROM users ORDER BY created_at ASC"
            )
        return [_row_to_user(r) for r in rows]

    async def find_by_id(self, user_id: str) -> Optional[User]:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, name, email, password_hash, role, is_active, created_at "
                "FROM users WHERE id = $1",
                user_id,
            )
        return _row_to_user(row) if row else None

    async def find_by_email(self, email: str) -> Optional[User]:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, name, email, password_hash, role, is_active, created_at "
                "FROM users WHERE email = $1",
                email,
            )
        return _row_to_user(row) if row else None

    async def create(
        self,
        name: str,
        email: str,
        password_hash: str,
        role: str = "USER",
    ) -> User:
        try:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    INSERT INTO users (name, email, password_hash, role)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id, name, email, password_hash, role, is_active, created_at
                    """,
                    name,
                    email,
                    password_hash,
                    role,
                )
        except asyncpg.PostgresError as exc:
            raise map_asyncpg_error("User", exc) from exc
        return _row_to_user(row)

    async def update(self, user: User) -> User:
        try:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    UPDATE users
                    SET name = $1, email = $2, password_hash = $3,
                        role = $4, is_active = $5
                    WHERE id = $6
                    RETURNING id, name, email, password_hash, role, is_active, created_at
                    """,
                    user.name,
                    user.email,
                    user.password_hash,
                    user.role,
                    user.is_active,
                    user.id,
                )
        except asyncpg.PostgresError as exc:
            raise map_asyncpg_error("User", exc) from exc
        if row is None:
            raise NotFoundError("User", user.id)
        return _row_to_user(row)

    async def delete(self, user_id: str) -> None:
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM users WHERE id = $1",
                user_id,
            )
        # asyncpg возвращает строку "DELETE N"
        if result == "DELETE 0":
            raise NotFoundError("User", user_id)
