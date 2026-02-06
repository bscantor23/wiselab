import pytest
from unittest.mock import AsyncMock, MagicMock
from src.domain.auth.models import User
from src.domain.auth.value_objects import Email
from src.infrastructure.auth.services.jwt import JWTService
from datetime import datetime
import uuid

@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.get_by_email = AsyncMock(return_value=None)
    repo.add = AsyncMock()
    return repo

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.email = Email("test@example.com")
    user.password_hash = "hash"
    user.is_active = True
    user.full_name = "Mock User"
    user.updated_at = datetime.now()
    user.created_at = datetime.now()
    return user
