from typing import Optional

from pydantic import BaseModel, Field


class CreateWorkspaceRequestDto(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = None
