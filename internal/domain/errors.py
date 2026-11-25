"""
Доменные исключения слоя бизнес-логики.

Репозитории и сервисы используют эти типы, чтобы верхние слои
не зависели от конкретной базы данных или HTTP-фреймворка.
"""


class DomainError(Exception):
    """Базовый класс всех доменных ошибок."""


class InvalidInputError(DomainError):
    """Входные данные нарушают бизнес-правило (400 Bad Request)."""


class NotFoundError(DomainError):
    """Запрошенная сущность не найдена в хранилище (404 Not Found)."""

    def __init__(self, entity: str, identity: object = "") -> None:
        super().__init__(f"{entity} with id={identity!r} not found")
        self.entity = entity
        self.identity = identity


class ConflictError(DomainError):
    """Конфликт состояния или нарушение уникальности (409 Conflict)."""


class AlreadyExistsError(ConflictError):
    """Нарушение ограничения уникальности — сущность уже существует (409 Conflict)."""

    def __init__(self, entity: str, field: str, value: object) -> None:
        super().__init__(f"{entity} with {field}={value!r} already exists")
        self.entity = entity
        self.field = field
        self.value = value


class DatabaseError(DomainError):
    """Непредвиденная ошибка при работе с базой данных (500 Internal Server Error)."""

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.cause = cause
