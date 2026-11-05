"""
Интерфейс репозитория категорий обращений.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from internal.domain.models import Category


class CategoryRepository(ABC):

    @abstractmethod
    async def find_all(self) -> List[Category]:
        """Вернуть все категории."""

    @abstractmethod
    async def find_by_id(self, category_id: str) -> Optional[Category]:
        """Вернуть категорию по UUID или None."""

    @abstractmethod
    async def create(self, title: str, description: Optional[str] = None) -> Category:
        """Создать категорию.

        Raises:
            AlreadyExistsError: если категория с таким title уже существует.
        """

    @abstractmethod
    async def delete(self, category_id: str) -> None:
        """Удалить категорию.

        Raises:
            NotFoundError: если категория не найдена.
        """
