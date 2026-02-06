import pytest
import pytest_asyncio
from httpx import AsyncClient
from src.infrastructure.database import get_db
from src.api.main import app

@pytest_asyncio.fixture
async def client(db_session):
    async def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
