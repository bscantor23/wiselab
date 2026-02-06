from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from src.domain.base import Entity
from src.domain.workspace.value_objects import WorkspaceRole


class WorkspaceMember(Entity):

    def __init__(
        self,
        workspace_id: UUID,
        user_id: UUID,
        role: WorkspaceRole,
        joined_at: Optional[datetime] = None,
        id: Optional[UUID] = None,
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
