"""
Доменные исключения слоя бизнес-логики.

Репозитории отображают низкоуровневые ошибки СУБД на эти типы,
чтобы сервисный слой не зависел от конкретной базы данных.
"""


class DomainError(Exception):
    """Базовый класс всех доменных ошибок."""


class NotFoundError(DomainError):
    """Запрошенная сущность не найдена в хранилище."""

    def __init__(self, entity: str, identity: object) -> None:
        super().__init__(f"{entity} with id={identity!r} not found")
        self.entity = entity
        self.identity = identity


class AlreadyExistsError(DomainError):
    """Нарушение ограничения уникальности — сущность уже существует."""

    def __init__(self, entity: str, field: str, value: object) -> None:
        super().__init__(f"{entity} with {field}={value!r} already exists")
        self.entity = entity
        self.field = field
        self.value = value


class DatabaseError(DomainError):
    """Непредвиденная ошибка при работе с базой данных."""

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.cause = cause
