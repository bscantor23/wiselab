from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional
from uuid import UUID

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    @abstractmethod
    async def add(self, entity: T) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[T]:
        pass

    @abstractmethod
    async def list(self) -> List[T]:
        pass

    @abstractmethod
    async def remove(self, id: UUID) -> None:
        pass
