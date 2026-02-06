from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.budget.models import Category


class CategoryRepository(ABC):
    @abstractmethod
    async def add(self, category: Category) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Category]:
        pass

    @abstractmethod
    async def get_by_name(self, name: str, workspace_id: Optional[UUID] = None) -> Optional[Category]:
        pass

    @abstractmethod
    async def list_defaults(self) -> List[Category]:
        pass

    @abstractmethod
    async def list_by_workspace(self, workspace_id: UUID) -> List[Category]:
        pass
