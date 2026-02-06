from uuid import UUID

from src.domain.auth.models import User
from src.domain.errors import UnauthorizedError, WorkspaceNotFoundError
from src.domain.workspace.models import Workspace
from src.domain.workspace.repositories import WorkspaceRepository


class GetWorkspace:
    def __init__(self, workspace_repo: WorkspaceRepository):
        self._repo = workspace_repo

    async def execute(self, workspace_id: UUID, user: User) -> Workspace:
        workspace = await self._repo.get_by_id(workspace_id)
        if not workspace:
            raise WorkspaceNotFoundError("Workspace not found")

        if workspace.owner_id == user.id:
            return workspace

        member = await self._repo.get_member(workspace_id, user.id)
        if not member:
            raise UnauthorizedError("User is not a member of this workspace")

        return workspace
