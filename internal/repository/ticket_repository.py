"""
Интерфейс репозитория тикетов (обращений).
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from internal.domain.models import Ticket


class TicketRepository(ABC):

    @abstractmethod
    async def find_all(self) -> List[Ticket]:
        """Вернуть все тикеты."""

    @abstractmethod
    async def find_by_id(self, ticket_id: str) -> Optional[Ticket]:
        """Вернуть тикет по UUID или None."""

    @abstractmethod
    async def find_by_requester(self, requester_id: str) -> List[Ticket]:
        """Вернуть все тикеты конкретного заявителя."""

    @abstractmethod
    async def create(
        self,
        subject: str,
        description: str,
        priority: str,
        category_id: str,
        requester_id: str,
        sla_policy_id: str,
        response_due_at: object,
        resolution_due_at: object,
    ) -> Ticket:
        """Создать тикет и вернуть сохранённую сущность.

        Raises:
            NotFoundError: если category_id, requester_id или sla_policy_id не существует.
        """

    @abstractmethod
    async def update_status(self, ticket_id: str, status: str) -> Ticket:
        """Обновить статус тикета.

        Raises:
            NotFoundError: если тикет не найден.
        """

    @abstractmethod
    async def delete(self, ticket_id: str) -> None:
        """Удалить тикет по UUID.

        Raises:
            NotFoundError: если тикет не найден.
        """
