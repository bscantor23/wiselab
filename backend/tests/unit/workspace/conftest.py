import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timezone

from src.domain.workspace.models import Workspace, WorkspaceMember
from src.domain.workspace.value_objects import WorkspaceRole
from src.domain.auth.models import User
from src.domain.auth.value_objects import Email

@pytest.fixture
def mock_workspace_repo():
    repo = MagicMock()
    repo.add = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.list_by_user = AsyncMock(return_value=[])
    repo.add_member = AsyncMock()
    repo.get_member = AsyncMock(return_value=None)
    repo.list_members = AsyncMock(return_value=[])
    repo.update_member = AsyncMock()
    repo.remove_member = AsyncMock()
    repo.update = AsyncMock()
    repo.remove = AsyncMock()
    return repo

@pytest.fixture
def mock_user_repo():
    repo = MagicMock()
    repo.get_by_email = AsyncMock(return_value=None)
    return repo

@pytest.fixture
def mock_user_entity():
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.email = Email("test@example.com")
    return user

@pytest.fixture
def mock_workspace_entity(mock_user_entity):
    return Workspace(
        id=uuid4(),
        name="Test Workspace",
        description="Test Desc",
        owner_id=mock_user_entity.id
    )

@pytest.fixture
def mock_member_entity(mock_workspace_entity, mock_user_entity):
    return WorkspaceMember(
        id=uuid4(),
        workspace_id=mock_workspace_entity.id,
        user_id=mock_user_entity.id,
        role=WorkspaceRole.OWNER
    )

@pytest.fixture
def mock_session():
    mock = AsyncMock()
    mock.commit = AsyncMock()
    mock.rollback = AsyncMock()
    return mock
