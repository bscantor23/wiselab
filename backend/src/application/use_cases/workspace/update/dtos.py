from typing import Optional

from pydantic import BaseModel, Field


class UpdateWorkspaceRequestDto(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = None
