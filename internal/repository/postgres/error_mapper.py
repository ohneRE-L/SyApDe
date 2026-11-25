"""
Вспомогательная функция: отображение исключений asyncpg → доменные ошибки.
"""

import asyncpg

from internal.domain.errors import (
    AlreadyExistsError,
    DatabaseError,
    InvalidInputError,
    NotFoundError,
)


def map_asyncpg_error(entity: str, exc: Exception) -> Exception:
    """Преобразует низкоуровневые ошибки asyncpg в доменные исключения.

    Args:
        entity: имя сущности (для сообщения об ошибке), например "User".
        exc:    исходное исключение asyncpg.

    Returns:
        Соответствующее доменное исключение.
    """
    if isinstance(exc, asyncpg.UniqueViolationError):
        detail: str = getattr(exc, "detail", "") or ""
        field = "unknown"
        value: object = ""
        if "Key (" in detail:
            try:
                field = detail.split("(")[1].split(")")[0]
                value = detail.split("=(")[1].split(")")[0]
            except IndexError:
                pass
        return AlreadyExistsError(entity, field, value)

    if isinstance(exc, asyncpg.ForeignKeyViolationError):
        detail = getattr(exc, "detail", "") or ""
        return NotFoundError(entity, detail)

    if isinstance(exc, asyncpg.NoDataFoundError):
        return NotFoundError(entity, "?")

    if isinstance(exc, (asyncpg.DataError, asyncpg.CheckViolationError)):
        return InvalidInputError(f"Invalid data for {entity}: {exc}")

    return DatabaseError(f"Unexpected database error for {entity}: {exc}", cause=exc)
