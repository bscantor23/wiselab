from uuid import UUID
from src.domain.workspace.repositories import WorkspaceRepository
from src.domain.workspace.value_objects import WorkspaceRole
from src.domain.auth.models import User
from src.domain.errors import WorkspaceNotFoundError, UnauthorizedError, MemberNotFoundError, ValidationError


class RemoveMember:
    def __init__(self, workspace_repo: WorkspaceRepository):
        self._repo = workspace_repo

    async def execute(
            self,
            workspace_id: UUID,
            member_user_id: UUID,
            current_user: User) -> None:
        workspace = await self._repo.get_by_id(workspace_id)
        if not workspace:
            raise WorkspaceNotFoundError("Workspace not found")

        # Permission Check
        has_permission = False
        if workspace.owner_id == current_user.id:
            has_permission = True
        else:
            admin_member = await self._repo.get_member(workspace_id, current_user.id)
            if admin_member and admin_member.role == WorkspaceRole.ADMIN:
                has_permission = True

        if not has_permission:
            raise UnauthorizedError(
                "Insufficient permissions to remove member")

        # Cannot remove Owner
        if workspace.owner_id == member_user_id:
            raise ValidationError("Cannot remove the workspace owner")

        member = await self._repo.get_member(workspace_id, member_user_id)
        if not member:
            raise MemberNotFoundError("Member not found in workspace")

        await self._repo.remove_member(workspace_id, member_user_id)
