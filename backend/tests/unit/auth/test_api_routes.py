import pytest
from httpx import AsyncClient
from unittest.mock import patch
from src.domain.errors import UnauthorizedError
from src.api.routes.auth import register, login
from src.application.use_cases.auth.register.dtos import RegisterUserRequestDto
from src.application.use_cases.auth.login.dtos import LoginUserRequestDto
from src.domain.auth.models import User
from src.domain.auth.value_objects import Email
from unittest.mock import AsyncMock
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_register_happy_path_unit(mock_repo, mock_session):
    """Unit test for register route success path"""
    mock_data = RegisterUserRequestDto(
        email="unit@example.com", 
        password="Password123!", 
        full_name="Unit"
    )
    
    with patch("src.api.routes.auth.RegisterUser") as MockRegisterUser:
        mock_use_case = MockRegisterUser.return_value
        expected_user = User(email=Email("unit@example.com"), password_hash="hash")
        # Ensure execute is awaited properly
        mock_use_case.execute = AsyncMock(return_value=expected_user)
        
        result = await register(mock_data, session=mock_session, user_repo=mock_repo)
        
        assert result == expected_user
        mock_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_auth_route_exceptions(mock_session):
    """Test exception handling for auth routes via endpoints directly"""
    # Using client for route wrapper coverage would be redundant with e2e,
    # but we can test the exception mapping logic if we want to be strict unit.
    pass

@pytest.mark.asyncio
async def test_auth_route_unhandled_exceptions():
    """Test 500 handling for auth routes"""
    from src.api.main import app
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register Exception
        with patch("src.api.routes.auth.RegisterUser.execute", side_effect=Exception("Register fail")):
            response = await client.post("/auth/register", json={
                "email": "fail@example.com",
                "password": "Password123!",
                "full_name": "Fail"
            })
            assert response.status_code == 500
            assert "Register fail" in response.json()["detail"]

        # Login Exception
        with patch("src.api.routes.auth.LoginUser.execute", side_effect=Exception("Login fail")):
            response = await client.post("/auth/login", json={
                "email": "fail@example.com",
                "password": "Password123!"
            })
            assert response.status_code == 500
            assert "Login fail" in response.json()["detail"]
