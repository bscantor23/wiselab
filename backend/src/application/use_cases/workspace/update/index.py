from uuid import UUID

from src.application.use_cases.workspace.update.dtos import UpdateWorkspaceRequestDto
from src.domain.auth.models import User
from src.domain.errors import ConflictError, UnauthorizedError, WorkspaceNotFoundError
from src.domain.workspace.models import Workspace
from src.domain.workspace.repositories import WorkspaceRepository
from src.domain.workspace.value_objects import WorkspaceRole


class UpdateWorkspace:
    def __init__(self, workspace_repo: WorkspaceRepository):
        self._repo = workspace_repo

    async def execute(
        self, workspace_id: UUID, user: User, data: UpdateWorkspaceRequestDto
    ) -> Workspace:
        workspace = await self._repo.get_by_id(workspace_id)
        if not workspace:
            raise WorkspaceNotFoundError("Workspace not found")

        is_owner = workspace.owner_id == user.id
        is_admin = False

        if not is_owner:
            member = await self._repo.get_member(workspace_id, user.id)
            if member and member.role == WorkspaceRole.ADMIN:
                is_admin = True

        if not (is_owner or is_admin):
            raise UnauthorizedError("Insufficient permissions to update workspace")

        if data.name != workspace.name:
            existing = await self._repo.get_by_name_and_owner(data.name, workspace.owner_id)
            if existing:
                raise ConflictError(f"Workspace with name '{data.name}' already exists for this owner")

        workspace.update_details(name=data.name, description=data.description)
        await self._repo.update(workspace)
        return workspace
