from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.auth.models import User
from src.domain.auth.value_objects import Email
from src.domain.auth.repositories import UserRepository
from src.infrastructure.auth.models import UserORM
from src.infrastructure.auth.mappers import UserMapper


class SQLUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, user: User) -> None:
        orm_user = UserMapper.to_orm(user)
        self._session.add(orm_user)

    async def get_by_id(self, id: UUID) -> Optional[User]:
        result = await self._session.execute(select(UserORM).filter_by(id=id))
        orm_user = result.scalar_one_or_none()
        return UserMapper.to_domain(orm_user) if orm_user else None

    async def get_by_email(self, email: Email) -> Optional[User]:
        result = await self._session.execute(select(UserORM).filter_by(email=email.value))
        orm_user = result.scalar_one_or_none()
        return UserMapper.to_domain(orm_user) if orm_user else None

    async def list(self) -> List[User]:
        result = await self._session.execute(select(UserORM))
        return [UserMapper.to_domain(orm_user) for orm_user in result.scalars()]

    async def remove(self, user: User) -> None:
        orm_user = await self._session.get(UserORM, user.id)
        if orm_user:
            await self._session.delete(orm_user)
