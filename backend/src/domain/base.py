from abc import ABC
from datetime import datetime
from typing import Optional
import uuid

class Entity(ABC):
    def __init__(self, id: Optional[uuid.UUID] = None):
        self._id = id or uuid.uuid4()
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()

    @property
    def id(self) -> uuid.UUID:
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
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
