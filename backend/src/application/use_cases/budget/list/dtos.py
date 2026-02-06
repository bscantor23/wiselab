from typing import List

from pydantic import BaseModel, ConfigDict

from src.application.use_cases.budget.create.dtos import BudgetResponseDto


class ListBudgetsResponseDto(BaseModel):
    items: List[BudgetResponseDto]
    total: int
    page: int
    size: int

    model_config = ConfigDict(from_attributes=True)
