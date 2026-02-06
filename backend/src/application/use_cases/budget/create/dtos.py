from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateBudgetRequestDto(BaseModel):
    workspace_id: UUID
    category_id: UUID
    limit_amount: float = Field(..., gt=0)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000)


class CategoryResponseDto(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    is_default: bool
    workspace_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class BudgetResponseDto(BaseModel):
    id: UUID
    workspace_id: UUID
    owner_id: UUID
    category_id: UUID
    limit_amount: float
    month: int
    year: int
    spent_amount: float = 0.0
    progress_percentage: float = 0.0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
