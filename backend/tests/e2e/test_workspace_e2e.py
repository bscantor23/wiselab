import pytest
import uuid
from httpx import AsyncClient
from src.infrastructure.auth.services.jwt import JWTService

@pytest.mark.asyncio
async def test_workspace_full_flow(client: AsyncClient):
    # 1. Setup: Register and Login to get access token
    user_data = {
        "email": f"workspace_e2e_{uuid.uuid4().hex[:6]}@example.com",
        "password": "Password123!",
        "full_name": "Workspace E2E User"
    }
    await client.post("/auth/register", json=user_data)
    
    login_response = await client.post("/auth/login", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    tokens = login_response.json()
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 2. Create Workspace
    workspace_data = {
        "name": "E2E Workspace",
        "description": "Created during E2E test"
    }
    response = await client.post("/workspaces", json=workspace_data, headers=headers)
    assert response.status_code == 201
    workspace = response.json()
    assert workspace["name"] == workspace_data["name"]
    workspace_id = workspace["id"]
    
    # 3. List Workspaces
    response = await client.get("/workspaces", headers=headers)
    assert response.status_code == 200
    workspaces = response.json()
    assert len(workspaces) >= 1
    assert any(w["id"] == workspace_id for w in workspaces)
    
    # 4. Get Workspace
    response = await client.get(f"/workspaces/{workspace_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == workspace_data["name"]
    
    # 5. Update Workspace
    update_data = {"name": "Updated E2E Workspace", "description": "Updated"}
    response = await client.put(f"/workspaces/{workspace_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]
    
    # 6. Invite Member
    # First create another user to invite
    other_user_data = {
        "email": f"member_e2e_{uuid.uuid4().hex[:6]}@example.com",
        "password": "Password123!",
        "full_name": "Member E2E"
    }
    await client.post("/auth/register", json=other_user_data)
    
    invite_data = {
        "email": other_user_data["email"],
        "role": "viewer"
    }
    response = await client.post(f"/workspaces/{workspace_id}/members", json=invite_data, headers=headers)
    assert response.status_code == 201
    member = response.json()
    other_user_id = member["user_id"]
    assert other_user_id is not None
    
    # 7. List Members
    response = await client.get(f"/workspaces/{workspace_id}/members", headers=headers)
    assert response.status_code == 200
    members = response.json()
    assert len(members) == 2 # Owner + invited member
    
    # 8. Update Member Role
    role_update = {"role": "admin"}
    response = await client.put(f"/workspaces/{workspace_id}/members/{other_user_id}", json=role_update, headers=headers)
    assert response.status_code == 200
    assert response.json()["role"] == "admin"
    
    # 9. Remove Member
    response = await client.delete(f"/workspaces/{workspace_id}/members/{other_user_id}", headers=headers)
    assert response.status_code == 204
    
    # 10. Delete Workspace
    response = await client.delete(f"/workspaces/{workspace_id}", headers=headers)
    assert response.status_code == 204
    
    # Verify deletion
    response = await client.get(f"/workspaces/{workspace_id}", headers=headers)
    assert response.status_code == 404
