from pydantic import BaseModel, Field


class UpdateBudgetRequestDto(BaseModel):
    limit_amount: float = Field(..., gt=0)
