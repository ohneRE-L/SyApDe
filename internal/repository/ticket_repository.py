from abc import ABC, abstractmethod
from typing import List, Optional

class TicketRepository(ABC):
    @abstractmethod
    def find_all(self) -> List[dict]:
        pass

    @abstractmethod
    def find_by_id(self, ticket_id: str) -> Optional[dict]:
        pass
