from uuid import UUID

from src.application.use_cases.workspace.members.invite.dtos import (
    InviteMemberRequestDto,
)
from src.domain.auth.models import User
from src.domain.auth.repositories import UserRepository
from src.domain.auth.value_objects import Email
from src.domain.errors import (
    NotFoundError,
    UnauthorizedError,
    ValidationError,
    WorkspaceNotFoundError,
)
from src.domain.workspace.models import WorkspaceMember
from src.domain.workspace.repositories import WorkspaceRepository
from src.domain.workspace.value_objects import WorkspaceRole


class InviteMember:
    def __init__(self, workspace_repo: WorkspaceRepository, user_repo: UserRepository):
        self._workspace_repo = workspace_repo
        self._user_repo = user_repo

    async def execute(
        self, workspace_id: UUID, current_user: User, data: InviteMemberRequestDto
    ) -> WorkspaceMember:
        workspace = await self._workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise WorkspaceNotFoundError("Workspace not found")

        has_permission = False
        if workspace.owner_id == current_user.id:
            has_permission = True
        else:
            inviter = await self._workspace_repo.get_member(
                workspace_id, current_user.id
            )
            if inviter and inviter.role == WorkspaceRole.ADMIN:
                has_permission = True

        if not has_permission:
            raise UnauthorizedError("Insufficient permissions to invite members")

        try:
            email_vo = Email(data.email)
        except ValidationError as e:
            raise ValidationError(str(e))

        user_to_invite = await self._user_repo.get_by_email(email_vo)
        if not user_to_invite:
            raise NotFoundError("User not found")

        if workspace.owner_id == user_to_invite.id:
            raise ValidationError("User is the owner of the workspace")

        existing_member = await self._workspace_repo.get_member(
            workspace_id, user_to_invite.id
        )
        if existing_member:
            raise ValidationError("User is already a member of the workspace")

        if data.role == WorkspaceRole.OWNER:
            raise ValidationError("Cannot assign OWNER role via invitation")

        new_member = WorkspaceMember(
            workspace_id=workspace.id, user_id=user_to_invite.id, role=data.role
        )

        await self._workspace_repo.add_member(new_member)
        return new_member
