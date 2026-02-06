from pydantic import BaseModel, Field
from typing import Optional


class UpdateWorkspaceRequestDto(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = None
