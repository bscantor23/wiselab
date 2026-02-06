import pytest
import uuid
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from src.infrastructure.auth.services.jwt import JWTService
from src.infrastructure.database import get_db

def test_jwt_service_with_delta():
    payload = {"sub": "user123"}
    delta = timedelta(minutes=10)
    token = JWTService.create_token(payload, expires_delta=delta)
    decoded = JWTService.decode_token(token)
    assert decoded["sub"] == "user123"

def test_jwt_refresh_token():
    payload = {"sub": "user123"}
    token = JWTService.create_token(payload, token_type="refresh")
    decoded = JWTService.decode_token(token)
    assert decoded["sub"] == "user123"
    assert decoded["type"] == "refresh"

@pytest.mark.asyncio
async def test_get_db_generator():
    mock_session = AsyncMock()
    mock_session_factory = MagicMock()
    with patch("src.infrastructure.database.async_session", mock_session_factory):
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        async for session in get_db():
            assert session == mock_session

def test_dto_email_validator_branch():
    from src.application.use_cases.auth.register.dtos import RegisterUserResponseDto
    from src.domain.auth.value_objects import Email
    
    data = {
        "id": uuid.uuid4(),
        "email": Email("test@example.com"),
        "full_name": "Test",
        "is_active": True
    }
    dto = RegisterUserResponseDto.model_validate(data)
    assert dto.email == "test@example.com"

@pytest.mark.asyncio
async def test_abstract_repository_coverage():
    from src.domain.repository import Repository
    from src.domain.auth.repositories import UserRepository
    
    class DummyRepo(Repository):
        async def add(self, entity): await super().add(entity)
        async def get_by_id(self, id): return await super().get_by_id(id)
        async def list(self): return await super().list()
        async def remove(self, entity): await super().remove(entity)

    dr = DummyRepo()
    await dr.add(None)
    await dr.get_by_id(None)
    await dr.list()
    await dr.remove(None)

    class DummyUserRepo(UserRepository):
        async def get_by_email(self, email): return await super().get_by_email(email)
        async def add(self, user): pass
        async def get_by_id(self, id): pass
        async def list(self): pass
        async def remove(self, user): pass

    dur = DummyUserRepo()
    await dur.get_by_email(None)
