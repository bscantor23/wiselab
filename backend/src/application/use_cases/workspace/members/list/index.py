from typing import List
from uuid import UUID

from src.domain.auth.models import User
from src.domain.errors import UnauthorizedError, WorkspaceNotFoundError
from src.domain.workspace.models import WorkspaceMember
from src.domain.workspace.repositories import WorkspaceRepository


class ListMembers:
    def __init__(self, workspace_repo: WorkspaceRepository):
        self._repo = workspace_repo

    async def execute(
        self, workspace_id: UUID, current_user: User
    ) -> List[WorkspaceMember]:
        workspace = await self._repo.get_by_id(workspace_id)
        if not workspace:
            raise WorkspaceNotFoundError("Workspace not found")

        if workspace.owner_id != current_user.id:
            member = await self._repo.get_member(workspace_id, current_user.id)
            if not member:
                raise UnauthorizedError("User is not a member of this workspace")

        return await self._repo.list_members(workspace_id)
