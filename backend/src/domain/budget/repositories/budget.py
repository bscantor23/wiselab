from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID

from src.domain.budget.models import Budget


class BudgetRepository(ABC):
    @abstractmethod
    async def add(self, budget: Budget) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Budget]:
        pass

    @abstractmethod
    async def get_by_category_period(
        self, workspace_id: UUID, category_id: UUID, month: int, year: int
    ) -> Optional[Budget]:
        pass

    @abstractmethod
    async def list_by_workspace(
        self,
        workspace_id: UUID,
        category_id: Optional[UUID] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[Budget], int]:
        pass

    @abstractmethod
    async def update(self, budget: Budget) -> None:
        pass

    @abstractmethod
    async def remove(self, budget: Budget) -> None:
        pass
