from pydantic import BaseModel

from src.domain.workspace.value_objects import WorkspaceRole


class InviteMemberRequestDto(BaseModel):
    email: str
    role: WorkspaceRole = WorkspaceRole.VIEWER
