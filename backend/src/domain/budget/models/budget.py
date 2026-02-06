from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from src.domain.base import Entity
from src.domain.errors import ValidationError


class Budget(Entity):
    def __init__(
        self,
        workspace_id: UUID,
        owner_id: UUID,
        category_id: UUID,
        limit_amount: float,
        month: int,
        year: int,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        deleted_at: Optional[datetime] = None,
    ):
        super().__init__(id)
        self._workspace_id = workspace_id
        self._owner_id = owner_id
        self._category_id = category_id
        self._limit_amount = limit_amount
        self._month = month
        self._year = year
        self._created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = updated_at or self._created_at
        self._deleted_at = deleted_at

        self.validate()

    @property
    def workspace_id(self) -> UUID:
        return self._workspace_id

    @property
    def owner_id(self) -> UUID:
        return self._owner_id

    @property
    def category_id(self) -> UUID:
        return self._category_id

    @property
    def limit_amount(self) -> float:
        return self._limit_amount

    @property
    def month(self) -> int:
        return self._month

    @property
    def year(self) -> int:
        return self._year

    @property
    def deleted_at(self) -> Optional[datetime]:
        return self._deleted_at

    def validate(self):
        if not self._category_id:
            raise ValidationError("Category ID is required")
        if self._limit_amount <= 0:
            raise ValidationError("Limit amount must be greater than zero")
        if not (1 <= self._month <= 12):
            raise ValidationError("Month must be between 1 and 12")
        if self._year < 2000:  # Simple validation for year
            raise ValidationError("Invalid year")

    def update_limit(self, new_limit: float):
        self._limit_amount = new_limit
        self.validate()
        self._updated_at = datetime.now(timezone.utc)

    def delete(self):
        self._deleted_at = datetime.now(timezone.utc)
        self._updated_at = self._deleted_at
