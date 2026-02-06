import pytest
from unittest.mock import AsyncMock
from src.api.dependencies.workspace import get_workspace_repository
from src.infrastructure.workspace.repositories import SQLWorkspaceRepository

@pytest.mark.asyncio
async def test_get_workspace_repository():
    session = AsyncMock()
    repo = await get_workspace_repository(session)
    assert isinstance(repo, SQLWorkspaceRepository)
    assert repo._session == session
