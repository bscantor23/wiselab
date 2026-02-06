from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from src.domain.base import Entity
from src.domain.auth.value_objects import Email


class User(Entity):
    def __init__(
        self,
        email: Email,
        password_hash: str,
        full_name: Optional[str] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        id: Optional[UUID] = None
    ):
        super().__init__(id)
        self._email = email
        self._password_hash = password_hash
        self._full_name = full_name
        self._is_active = is_active
        self._created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = updated_at or datetime.now(timezone.utc)

    @property
    def email(self) -> Email:
        return self._email

    @property
    def password_hash(self) -> str:
        return self._password_hash

    @property
    def full_name(self) -> Optional[str]:
        return self._full_name

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def update_profile(self, full_name: Optional[str] = None):
        if full_name:
            self._full_name = full_name
        self._updated_at = datetime.now(timezone.utc)

    def deactivate(self):
        self._is_active = False
        self._updated_at = datetime.now(timezone.utc)

    def activate(self):
        self._is_active = True
        self._updated_at = datetime.now(timezone.utc)
