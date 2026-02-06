from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from src.domain.base import Entity
from src.domain.workspace.value_objects import WorkspaceRole


class WorkspaceMember(Entity):

    def __init__(
        self,
        workspace_id: UUID,
        user_id: UUID,
        role: WorkspaceRole,
        joined_at: Optional[datetime] = None,
        id: Optional[UUID] = None
    ):
        super().__init__(id)
        self._workspace_id = workspace_id
        self._user_id = user_id
        self._role = role
        self._joined_at = joined_at or datetime.now(timezone.utc)

    @property
    def workspace_id(self) -> UUID:
        return self._workspace_id

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def role(self) -> WorkspaceRole:
        return self._role

    @property
    def joined_at(self) -> datetime:
        return self._joined_at

    def change_role(self, new_role: WorkspaceRole):
        self._role = new_role


class Workspace(Entity):
    def __init__(
        self,
        name: str,
        owner_id: UUID,
        description: Optional[str] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        id: Optional[UUID] = None
    ):
        super().__init__(id)
        self._name = name
        self._description = description
        self._owner_id = owner_id
        self._is_active = is_active
        self._created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = updated_at or datetime.now(timezone.utc)

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def owner_id(self) -> UUID:
        return self._owner_id

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def update_details(
            self,
            name: Optional[str] = None,
            description: Optional[str] = None):
        if name:
            self._name = name
        if description is not None:
            self._description = description
        self._updated_at = datetime.now(timezone.utc)
