from uuid import UUID

from src.domain.auth.models import User
from src.domain.errors import UnauthorizedError, WorkspaceNotFoundError
from src.domain.workspace.repositories import WorkspaceRepository


class DeleteWorkspace:
    def __init__(self, workspace_repo: WorkspaceRepository):
        self._repo = workspace_repo

    async def execute(self, workspace_id: UUID, user: User) -> None:
        workspace = await self._repo.get_by_id(workspace_id)
        if not workspace:
            raise WorkspaceNotFoundError("Workspace not found")

        if workspace.owner_id != user.id:
            raise UnauthorizedError("Only the workspace owner can delete the workspace")

        await self._repo.remove(workspace)
