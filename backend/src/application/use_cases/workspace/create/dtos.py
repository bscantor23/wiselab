from pydantic import BaseModel, Field
from typing import Optional


class CreateWorkspaceRequestDto(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = None
