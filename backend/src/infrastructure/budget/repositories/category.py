from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.budget.models import Category
from src.domain.budget.repositories import CategoryRepository
from src.infrastructure.budget.mappers.category import CategoryMapper
from src.infrastructure.budget.models.category import CategoryORM


class SQLCategoryRepository(CategoryRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, category: Category) -> None:
        orm_category = CategoryMapper.to_orm(category)
        self._session.add(orm_category)

    async def get_by_id(self, id: UUID) -> Optional[Category]:
        stmt = select(CategoryORM).where(CategoryORM.id == id)
        result = await self._session.execute(stmt)
        orm_category = result.scalar_one_or_none()
        if not orm_category:
            return None
        return CategoryMapper.to_domain(orm_category)

    async def get_by_name(self, name: str, workspace_id: Optional[UUID] = None) -> Optional[Category]:
        filters = [CategoryORM.name == name]
        if workspace_id:
            filters.append(or_(CategoryORM.workspace_id == workspace_id, CategoryORM.is_default == True))
        else:
            filters.append(CategoryORM.is_default == True)
            
        stmt = select(CategoryORM).where(and_(*filters)).order_by(CategoryORM.is_default.desc())
        result = await self._session.execute(stmt)
        orm_category = result.first()
        if not orm_category:
            return None
        return CategoryMapper.to_domain(orm_category[0])

    async def list_defaults(self) -> List[Category]:
        stmt = select(CategoryORM).where(CategoryORM.is_default == True)
        result = await self._session.execute(stmt)
        return [CategoryMapper.to_domain(orm) for orm in result.scalars()]

    async def list_by_workspace(self, workspace_id: UUID) -> List[Category]:
        stmt = select(CategoryORM).where(
            or_(CategoryORM.workspace_id == workspace_id, CategoryORM.is_default == True)
        )
        result = await self._session.execute(stmt)
        return [CategoryMapper.to_domain(orm) for orm in result.scalars()]
