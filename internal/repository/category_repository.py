"""
Интерфейс репозитория категорий обращений.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from internal.domain.models import Category


class CategoryRepository(ABC):

    @abstractmethod
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Category]:
        """Вернуть категории с пагинацией."""

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
    async def update(self, category: Category) -> Category:
        """Обновить категорию.

        Raises:
            NotFoundError: если категория не найдена.
            AlreadyExistsError: если новое название уже занято.
        """

    @abstractmethod
    async def delete(self, category_id: str) -> None:
        """Удалить категорию.

        Raises:
            NotFoundError: если категория не найдена.
            ConflictError: если на категорию ссылаются существующие тикеты.
        """
