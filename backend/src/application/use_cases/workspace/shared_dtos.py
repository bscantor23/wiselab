from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.domain.workspace.value_objects import WorkspaceRole


class WorkspaceResponseDto(BaseModel):
    """Shared response DTO for workspace operations"""

    id: UUID
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    owner_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkspaceMemberResponseDto(BaseModel):
    """Shared response DTO for workspace member operations"""

    id: Optional[UUID]
    workspace_id: UUID
    user_id: UUID
    role: WorkspaceRole
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)
