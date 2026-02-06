
from uuid import UUID
from src.domain.workspace.repositories import WorkspaceRepository
from src.domain.workspace.models import WorkspaceMember
from src.domain.workspace.value_objects import WorkspaceRole
from src.domain.auth.models import User
from src.application.use_cases.workspace.members.update.dtos import UpdateMemberRoleRequestDto
from src.domain.errors import WorkspaceNotFoundError, UnauthorizedError, MemberNotFoundError, ValidationError


class UpdateMemberRole:
    def __init__(self, workspace_repo: WorkspaceRepository):
        self._repo = workspace_repo

    async def execute(
        self,
        workspace_id: UUID,
        member_user_id: UUID,
        current_user: User,
        data: UpdateMemberRoleRequestDto
    ) -> WorkspaceMember:

        workspace = await self._repo.get_by_id(workspace_id)
        if not workspace:
            raise WorkspaceNotFoundError("Workspace not found")

        # Permission check: Owner or Admin
        has_permission = False
        if workspace.owner_id == current_user.id:
            has_permission = True
        else:
            inviter = await self._repo.get_member(workspace_id, current_user.id)
            if inviter and inviter.role == WorkspaceRole.ADMIN:
                has_permission = True

        if not has_permission:
            raise UnauthorizedError(
                "Insufficient permissions to update member role")

        # Target member check
        if workspace.owner_id == member_user_id:
            raise ValidationError(
                "Cannot update the role of the workspace owner")

        member = await self._repo.get_member(workspace_id, member_user_id)
        if not member:
            raise MemberNotFoundError("Member not found")

        if data.role == WorkspaceRole.OWNER:
            raise ValidationError(
                "Cannot assign OWNER role via update. Transfer ownership instead.")

        member.change_role(data.role)
        await self._repo.update_member(member)
        return member
