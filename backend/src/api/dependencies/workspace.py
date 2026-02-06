from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database import get_db
from src.infrastructure.workspace.repositories import SQLWorkspaceRepository


async def get_workspace_repository(
    session: AsyncSession = Depends(get_db),
) -> SQLWorkspaceRepository:
    return SQLWorkspaceRepository(session)
