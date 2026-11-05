"""
Интерфейс репозитория пользователей.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from internal.domain.models import User


class UserRepository(ABC):

    @abstractmethod
    async def find_all(self) -> List[User]:
        """Вернуть всех пользователей."""

    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Вернуть пользователя по UUID или None."""

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        """Вернуть пользователя по e-mail или None."""

    @abstractmethod
    async def create(
        self,
        name: str,
        email: str,
        password_hash: str,
        role: str = "USER",
    ) -> User:
        """Создать нового пользователя и вернуть сохранённую сущность.

        Raises:
            AlreadyExistsError: если email уже занят.
        """

    @abstractmethod
    async def update(self, user: User) -> User:
        """Обновить данные пользователя.

        Raises:
            NotFoundError: если пользователь не найден.
        """

    @abstractmethod
    async def delete(self, user_id: str) -> None:
        """Удалить пользователя по UUID.

        Raises:
            NotFoundError: если пользователь не найден.
        """
