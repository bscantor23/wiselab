from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.budget.models import Budget
from src.domain.budget.repositories import BudgetRepository
from src.infrastructure.budget.mappers import BudgetMapper
from src.infrastructure.budget.models import BudgetORM


class SQLBudgetRepository(BudgetRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, budget: Budget) -> None:
        orm_budget = BudgetMapper.to_orm(budget)
        self._session.add(orm_budget)

    async def get_by_id(self, id: UUID) -> Optional[Budget]:
        stmt = select(BudgetORM).where(
            and_(BudgetORM.id == id, BudgetORM.deleted_at.is_(None))
        )
        result = await self._session.execute(stmt)
        orm_budget = result.scalar_one_or_none()
        if not orm_budget:
            return None
        return BudgetMapper.to_domain(orm_budget)

    async def get_by_category_period(
        self, workspace_id: UUID, category_id: UUID, month: int, year: int
    ) -> Optional[Budget]:
        stmt = select(BudgetORM).where(
            and_(
                BudgetORM.workspace_id == workspace_id,
                BudgetORM.category_id == category_id,
                BudgetORM.month == month,
                BudgetORM.year == year,
                BudgetORM.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        orm_budget = result.scalar_one_or_none()
        if not orm_budget:
            return None
        return BudgetMapper.to_domain(orm_budget)

    async def list_by_workspace(
        self,
        workspace_id: UUID,
        category_id: Optional[UUID] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[Budget], int]:
        filters = [
            BudgetORM.workspace_id == workspace_id,
            BudgetORM.deleted_at.is_(None),
        ]
        if category_id:
            filters.append(BudgetORM.category_id == category_id)
        if month:
            filters.append(BudgetORM.month == month)
        if year:
            filters.append(BudgetORM.year == year)

        # Count total
        count_stmt = select(func.count()).select_from(BudgetORM).where(and_(*filters))
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        # Get page
        stmt = select(BudgetORM).where(and_(*filters)).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return [BudgetMapper.to_domain(orm) for orm in result.scalars()], total

    async def update(self, budget: Budget) -> None:
        stmt = (
            update(BudgetORM)
            .where(BudgetORM.id == budget.id)
            .values(
                limit_amount=budget.limit_amount,
                updated_at=budget.updated_at,
                deleted_at=budget.deleted_at,
            )
        )
        await self._session.execute(stmt)

    async def remove(self, budget: Budget) -> None:
        # Soft delete
        stmt = (
            update(BudgetORM)
            .where(BudgetORM.id == budget.id)
            .values(deleted_at=budget.deleted_at, updated_at=budget.updated_at)
        )
        await self._session.execute(stmt)
