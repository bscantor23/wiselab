import pytest
from unittest.mock import AsyncMock
from src.api.dependencies.auth import get_user_repository
from src.infrastructure.auth.repositories import SQLUserRepository

@pytest.mark.asyncio
async def test_get_user_repository():
    session = AsyncMock()
    repo = await get_user_repository(session)
    assert isinstance(repo, SQLUserRepository)
    assert repo._session == session
