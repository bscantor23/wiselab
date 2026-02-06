import pytest
import uuid
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_budget_full_flow(client: AsyncClient):
    # 1. Setup: Register and Login
    email = f"budget_e2e_{uuid.uuid4().hex[:6]}@example.com"
    user_data = {
        "email": email,
        "password": "Password123!",
        "full_name": "Budget E2E User"
    }
    await client.post("/api/auth/register", json=user_data)
    
    login_response = await client.post("/api/auth/login", json={
        "email": email,
        "password": user_data["password"]
    })
    tokens = login_response.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # 2. Create Workspace
    ws_resp = await client.post("/api/workspaces", json={"name": "E2E WS"}, headers=headers)
    workspace_id = ws_resp.json()["id"]

    # 3. Get Categories
    cat_resp = await client.get("/api/budgets/categories", headers=headers)
    assert cat_resp.status_code == 200
    categories = cat_resp.json()
    assert len(categories) > 0
    category_id = categories[0]["id"]

    # 4. Create Budget
    budget_data = {
        "workspace_id": workspace_id,
        "category_id": category_id,
        "limit_amount": 1000.0,
        "month": 5,
        "year": 2024
    }
    response = await client.post("/api/budgets", json=budget_data, headers=headers)
    assert response.status_code == 201
    budget = response.json()
    assert budget["category_id"] == category_id
    budget_id = budget["id"]

    # 5. Get Budget
    response = await client.get(f"/api/budgets/{budget_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["limit_amount"] == 1000.0
    assert response.json()["spent_amount"] == 0.0 # Mocked

    # 6. List Budgets
    response = await client.get(f"/api/budgets?workspace_id={workspace_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(b["id"] == budget_id for b in data["items"])

    # 7. Update Budget
    response = await client.put(f"/api/budgets/{budget_id}", json={"limit_amount": 1200.0}, headers=headers)
    assert response.status_code == 200
    assert response.json()["limit_amount"] == 1200.0

    # 8. Delete Budget
    response = await client.delete(f"/api/budgets/{budget_id}", headers=headers)
    assert response.status_code == 204

    # 9. Verify deletion
    response = await client.get(f"/api/budgets/{budget_id}", headers=headers)
    assert response.status_code == 404
