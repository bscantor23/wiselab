import pytest
import uuid
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from unittest.mock import AsyncMock, patch
from src.api.dependencies.auth import get_current_user
from src.infrastructure.auth.services.jwt import JWTService


@pytest.mark.asyncio
async def test_get_current_user_success(mock_repo, mock_user, mock_session):
    """Test successful user retrieval from token"""
    mock_repo.get_by_id = AsyncMock(return_value=mock_user)
    token = JWTService.create_token({"sub": str(mock_user.id)}, token_type="access")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with patch("src.api.dependencies.auth.SQLUserRepository", return_value=mock_repo):
        result = await get_current_user(credentials=credentials, session=mock_session)
        assert result == mock_user


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_session):
    """Test 401 on invalid token"""
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid")
    with pytest.raises(HTTPException) as exc:
        await get_current_user(credentials=credentials, session=mock_session)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_missing_sub(mock_session):
    """Test 401 when sub is missing from payload"""
    token = JWTService.create_token({}, token_type="access")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    with pytest.raises(HTTPException) as exc:
        await get_current_user(credentials=credentials, session=mock_session)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_user_not_found(mock_repo, mock_session):
    """Test 401 when user id in token doesn't exist"""
    mock_repo.get_by_id = AsyncMock(return_value=None)
    token = JWTService.create_token({"sub": str(uuid.uuid4())}, token_type="access")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with patch("src.api.dependencies.auth.SQLUserRepository", return_value=mock_repo):
        with pytest.raises(HTTPException) as exc:
            await get_current_user(credentials=credentials, session=mock_session)
        assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_deactivated(mock_repo, mock_user, mock_session):
    """Test 403 when user is inactive"""
    mock_user.is_active = False
    mock_repo.get_by_id = AsyncMock(return_value=mock_user)
    token = JWTService.create_token({"sub": str(mock_user.id)}, token_type="access")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with patch("src.api.dependencies.auth.SQLUserRepository", return_value=mock_repo):
        with pytest.raises(HTTPException) as exc:
            await get_current_user(credentials=credentials, session=mock_session)
        assert exc.value.status_code == 403

