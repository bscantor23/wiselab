from abc import ABC, abstractmethod
from uuid import UUID


class MovementService(ABC):
    @abstractmethod
    async def get_spent_amount(
        self, workspace_id: UUID, category_id: UUID, month: int, year: int
    ) -> float:
        """Calculates the sum of all expense movements for a category in a period."""


class MockMovementService(MovementService):
    async def get_spent_amount(
        self, workspace_id: UUID, category_id: UUID, month: int, year: int
    ) -> float:
        return 0.0
