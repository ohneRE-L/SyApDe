"""
Интерфейс репозитория регламентов SLA.
"""

from abc import ABC, abstractmethod
from typing import Optional

from internal.domain.models import SlaPolicy


class SlaPolicyRepository(ABC):

    @abstractmethod
    async def find_by_priority(self, priority: str) -> Optional[SlaPolicy]:
        """Найти регламент SLA по приоритету ('LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL')."""
