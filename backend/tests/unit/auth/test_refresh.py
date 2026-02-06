import pytest
import uuid
from datetime import timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException

from src.application.use_cases.auth.refresh.index import RefreshToken
from src.application.use_cases.auth.refresh.dtos import RefreshTokenRequestDto
from src.infrastructure.auth.services.jwt import JWTService
from src.domain.errors import UnauthorizedError
from src.api.routes.auth import refresh
from jose import JWTError

@pytest.mark.asyncio
async def test_refresh_token_success(mock_repo, mock_user):
    """Test successful token refresh flow"""
    mock_repo.get_by_id = AsyncMock(return_value=mock_user)
    use_case = RefreshToken(mock_repo)
    
    token = JWTService.create_token({"sub": str(mock_user.id)}, token_type="refresh")
    result = await use_case.execute(RefreshTokenRequestDto(refresh_token=token))
    
    assert result.access_token is not None
    assert result.refresh_token is not None

@pytest.mark.asyncio
async def test_refresh_token_user_not_found(mock_repo):
    """Test error when user from token doesn't exist"""
    mock_repo.get_by_id = AsyncMock(return_value=None)
    use_case = RefreshToken(mock_repo)
    
    token = JWTService.create_token({"sub": str(uuid.uuid4())}, token_type="refresh")
    
    with pytest.raises(UnauthorizedError, match="User not found or inactive"):
        await use_case.execute(RefreshTokenRequestDto(refresh_token=token))

@pytest.mark.asyncio
async def test_refresh_token_user_inactive(mock_repo, mock_user):
    """Test error when user is inactive"""
    mock_user.is_active = False
    mock_repo.get_by_id = AsyncMock(return_value=mock_user)
    use_case = RefreshToken(mock_repo)
    
    token = JWTService.create_token({"sub": str(mock_user.id)}, token_type="refresh")
    
    with pytest.raises(UnauthorizedError, match="User not found or inactive"):
        await use_case.execute(RefreshTokenRequestDto(refresh_token=token))

@pytest.mark.asyncio
async def test_refresh_token_wrong_type(mock_repo):
    """Test error when verifying access token as refresh token"""
    use_case = RefreshToken(mock_repo)
    token = JWTService.create_token({"sub": str(uuid.uuid4())}, token_type="access")
    
    with pytest.raises(UnauthorizedError, match="Invalid refresh token"):
        await use_case.execute(RefreshTokenRequestDto(refresh_token=token))

@pytest.mark.asyncio
async def test_refresh_token_expired(mock_repo):
    """Test error when verifying expired refresh token"""
    use_case = RefreshToken(mock_repo)
    token = JWTService.create_token(
        {"sub": str(uuid.uuid4())}, 
        expires_delta=timedelta(seconds=-1), 
        token_type="refresh"
    )
    
    with pytest.raises(UnauthorizedError, match="Invalid refresh token"):
        await use_case.execute(RefreshTokenRequestDto(refresh_token=token))

@pytest.mark.asyncio
async def test_refresh_token_jwt_error(mock_repo):
    """Test error when JWT decoding fails unexpectedly"""
    use_case = RefreshToken(mock_repo)
    with patch("src.infrastructure.auth.services.jwt.JWTService.decode_token", side_effect=JWTError()):
        with pytest.raises(UnauthorizedError, match="Invalid refresh token"):
            await use_case.execute(RefreshTokenRequestDto(refresh_token="invalid"))

@pytest.mark.asyncio
async def test_refresh_endpoint_exception_handlers(mock_repo):
    """Test HTTP exception mapping in refresh endpoint"""
    mock_data = RefreshTokenRequestDto(refresh_token="token")
    
    # Test 401 Unauthorized mapping
    with patch("src.api.routes.auth.RefreshToken") as MockRefreshToken:
        mock_use_case = MockRefreshToken.return_value
        mock_use_case.execute.side_effect = UnauthorizedError("Invalid token")
        
        try:
            await refresh(mock_data, user_repo=mock_repo)
            assert False, "Should raise HTTPException"
        except HTTPException as e:
            assert e.status_code == 401
            assert "Invalid token" in e.detail

    # Test 500 mapping
    with patch("src.api.routes.auth.RefreshToken.execute", side_effect=Exception("Crash")):
        try:
            await refresh(mock_data, user_repo=mock_repo)
            assert False, "Should raise HTTPException"
        except HTTPException as e:
            assert e.status_code == 500
            assert "Crash" in e.detail
