import pytest
from httpx import AsyncClient
from unittest.mock import patch
from src.domain.errors import ValidationError, UnauthorizedError

@pytest.mark.asyncio
async def test_auth_full_flow(client: AsyncClient):
    # 1. Register with complex password
    user_data = {
        "email": "fullflow@example.com",
        "password": "Password123!",
        "full_name": "Full Flow User"
    }
    
    # 1.1 Try with weak password (should fail at Pydantic level)
    weak_data = user_data.copy()
    weak_data["password"] = "12345678"
    response = await client.post("/auth/register", json=weak_data)
    assert response.status_code == 422 
    
    # 1.2 Valid registration
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    
    # 2. Login
    login_data = {
        "email": "fullflow@example.com",
        "password": "Password123!"
    }
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]



    # 4. Refresh token
    refresh_data = {"refresh_token": refresh_token}
    # Small delay to ensure exp/iat difference if it was too fast
    import asyncio
    await asyncio.sleep(0.1) 
    response = await client.post("/auth/refresh", json=refresh_data)
    assert response.status_code == 200
    new_tokens = response.json()
    assert "access_token" in new_tokens
    assert new_tokens["access_token"] is not None
    assert "refresh_token" in new_tokens

    # 5. Login with wrong password (should fail)
    login_data["password"] = "wrongpassword"
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

@pytest.mark.asyncio
async def test_auth_route_exceptions(client: AsyncClient):
    # Test ValidationError in /register
    with patch("src.api.routes.auth.RegisterUser.execute", side_effect=ValidationError("Simulated validation error")):
        response = await client.post("/auth/register", json={
            "email": "valid@example.com",
            "password": "Password123!",
            "full_name": "Test"
        })
        assert response.status_code == 400
        assert "Simulated validation error" in response.json()["detail"]

    # Test Exception in /register
    with patch("src.api.routes.auth.RegisterUser.execute", side_effect=Exception("Simulated crash")):
        response = await client.post("/auth/register", json={
            "email": "valid@example.com",
            "password": "Password123!",
            "full_name": "Test"
        })
        assert response.status_code == 500
        assert "Simulated crash" in response.json()["detail"]

    # Test UnauthorizedError in /login
    with patch("src.api.routes.auth.LoginUser.execute", side_effect=UnauthorizedError("Account deactivated")):
        response = await client.post("/auth/login", json={
            "email": "valid@example.com",
            "password": "Password123!"
        })
        assert response.status_code == 401
        assert "Account deactivated" in response.json()["detail"]
