from pydantic import BaseModel

from src.domain.workspace.value_objects import WorkspaceRole


class UpdateMemberRoleRequestDto(BaseModel):
    role: WorkspaceRole
