from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from src.domain.base import Entity
from src.domain.errors import ValidationError


class Category(Entity):
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        is_default: bool = False,
        workspace_id: Optional[UUID] = None,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__(id)
        self._name = name
        self._description = description
        self._is_default = is_default
        self._workspace_id = workspace_id
        self._created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = updated_at or self._created_at

        self.validate()

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def is_default(self) -> bool:
        return self._is_default

    @property
    def workspace_id(self) -> Optional[UUID]:
        return self._workspace_id

    def validate(self):
        if not self._name or not self._name.strip():
            raise ValidationError("Category name cannot be empty")
        if len(self._name) > 50:
            raise ValidationError("Category name is too long")

    def update_details(self, name: str, description: Optional[str] = None):
        self._name = name
        self._description = description
        self.validate()
        self._updated_at = datetime.now(timezone.utc)
