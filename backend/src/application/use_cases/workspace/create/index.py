from src.domain.workspace.models import Workspace, WorkspaceMember
from src.domain.workspace.value_objects import WorkspaceRole
from src.domain.workspace.repositories import WorkspaceRepository
from src.application.use_cases.workspace.create.dtos import CreateWorkspaceRequestDto
from src.domain.auth.models import User


class CreateWorkspace:
    def __init__(self, workspace_repo: WorkspaceRepository):
        self._repo = workspace_repo

    async def execute(
            self,
            user: User,
            data: CreateWorkspaceRequestDto) -> Workspace:
        # Create workspace entity
        workspace = Workspace(
            name=data.name,
            description=data.description,
            owner_id=user.id
        )

        # Add creator as owner member
        owner_member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=user.id,
            role=WorkspaceRole.OWNER
        )

        await self._repo.add(workspace)
        await self._repo.add_member(owner_member)

        return workspace
