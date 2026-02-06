from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.budget.movement_service import (
    MockMovementService,
    MovementService,
)
from src.domain.budget.repositories import BudgetRepository, CategoryRepository
from src.infrastructure.budget.repositories import (
    SQLBudgetRepository,
    SQLCategoryRepository,
)
from src.infrastructure.database import get_db


async def get_budget_repository(
    session: AsyncSession = Depends(get_db),
) -> BudgetRepository:
    return SQLBudgetRepository(session)


async def get_category_repository(
    session: AsyncSession = Depends(get_db),
) -> CategoryRepository:
    return SQLCategoryRepository(session)


async def get_movement_service() -> MovementService:
    return MockMovementService()
