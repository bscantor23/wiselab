from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4


class Entity:
    def __init__(self, id: Optional[UUID] = None):
        self._id = id or uuid4()
        self._created_at = datetime.now(timezone.utc)
        self._updated_at = self._created_at

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
