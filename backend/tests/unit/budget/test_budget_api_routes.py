import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from fastapi import status

from src.api.main import app
from src.api.dependencies.auth import get_current_user
from src.domain.auth.models import User
from src.domain.budget.models import Budget
from src.domain.errors import NotFoundError, UnauthorizedError, ConflictError, ValidationError

@pytest.fixture
def user():
    user = MagicMock(spec=User)
    user.id = uuid4()
    return user

@pytest.fixture
def mock_db_session():
    mock = AsyncMock()
    mock.commit = AsyncMock()
    mock.rollback = AsyncMock()
    return mock

from datetime import datetime
import pytest_asyncio

@pytest.fixture
def mock_budget_repo():
    return AsyncMock()

@pytest.fixture
def mock_category_repo():
    return AsyncMock()

@pytest.fixture
def mock_workspace_repo():
    return AsyncMock()

@pytest.fixture
def mock_movement_service():
    return AsyncMock()

@pytest_asyncio.fixture
async def client(user, mock_db_session, mock_budget_repo, mock_category_repo, mock_workspace_repo, mock_movement_service):
    # Override dependencies
    app.dependency_overrides[get_current_user] = lambda: user
    
    # We also need to override get_db to avoid real DB connection attempt
    from src.infrastructure.database import get_db
    app.dependency_overrides[get_db] = lambda: mock_db_session
    
    # Repositories are dependencies too, we should override them to return Mocks
    # so that the route injection works, even if we patch valid usecases.
    from src.api.dependencies.budget import get_budget_repository, get_category_repository, get_movement_service
    from src.api.dependencies.workspace import get_workspace_repository
    
    app.dependency_overrides[get_budget_repository] = lambda: mock_budget_repo
    app.dependency_overrides[get_category_repository] = lambda: mock_category_repo
    app.dependency_overrides[get_workspace_repository] = lambda: mock_workspace_repo
    app.dependency_overrides[get_movement_service] = lambda: mock_movement_service

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_create_budget_success(client, user):
    payload = {
        "workspace_id": str(uuid4()),
        "category_id": str(uuid4()),
        "limit_amount": 1000.0,
        "month": 10,
        "year": 2023
    }

    with patch("src.api.routes.budget.CreateBudget") as MockUseClass:
        mock_instance = MockUseClass.return_value
        expected_budget = MagicMock(spec=Budget)
        expected_budget.id = uuid4()
        expected_budget.workspace_id = uuid4()
        expected_budget.owner_id = user.id
        expected_budget.category_id = uuid4()
        expected_budget.limit_amount = 1000.0
        expected_budget.month = 10
        expected_budget.year = 2023
        expected_budget.created_at = datetime.now()
        expected_budget.updated_at = datetime.now()
        
        mock_instance.execute = AsyncMock(return_value=expected_budget)

        response = await client.post("/budgets", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == str(expected_budget.id)
        assert data["limit_amount"] == 1000.0

@pytest.mark.asyncio
async def test_create_budget_unauthorized(client):
    payload = {
        "workspace_id": str(uuid4()),
        "category_id": str(uuid4()),
        "limit_amount": 1000.0,
        "month": 10,
        "year": 2023
    }
    
    with patch("src.api.routes.budget.CreateBudget") as MockUseClass:
        mock_instance = MockUseClass.return_value
        mock_instance.execute = AsyncMock(side_effect=UnauthorizedError("Access denied"))

        response = await client.post("/budgets", json=payload)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Access denied"

@pytest.mark.asyncio
async def test_create_budget_conflict(client):
    payload = {
        "workspace_id": str(uuid4()),
        "category_id": str(uuid4()),
        "limit_amount": 1000.0,
        "month": 10,
        "year": 2023
    }
    
    with patch("src.api.routes.budget.CreateBudget") as MockUseClass:
        mock_instance = MockUseClass.return_value
        mock_instance.execute = AsyncMock(side_effect=ConflictError("Exists"))

        response = await client.post("/budgets", json=payload)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Exists"

@pytest.mark.asyncio
async def test_get_budget_success(client):
    budget_id = str(uuid4())
    
    with patch("src.api.routes.budget.GetBudget") as MockUseClass:
        mock_instance = MockUseClass.return_value
        budget = MagicMock(spec=Budget)
        budget.id = budget_id
        budget.limit_amount = 1000.0
        budget.year = 2023
        budget.month = 10
        budget.workspace_id = uuid4()
        budget.owner_id = uuid4()
        budget.category_id = uuid4()
        budget.created_at = datetime.now()
        budget.updated_at = datetime.now()
        
        mock_instance.execute = AsyncMock(return_value=(budget, 500.0, 50.0))

        response = await client.get(f"/budgets/{budget_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["spent_amount"] == 500.0
        assert data["progress_percentage"] == 50.0

@pytest.mark.asyncio
async def test_get_budget_not_found(client):
    budget_id = str(uuid4())
    
    with patch("src.api.routes.budget.GetBudget") as MockUseClass:
        mock_instance = MockUseClass.return_value
        mock_instance.execute = AsyncMock(side_effect=NotFoundError("Not found"))

        response = await client.get(f"/budgets/{budget_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_list_budgets_success(client):
    workspace_id = str(uuid4())
    
    with patch("src.api.routes.budget.ListBudgets") as MockUseClass:
        mock_instance = MockUseClass.return_value
        
        budget = MagicMock(spec=Budget)
        budget.id = uuid4()
        budget.limit_amount = 1000.0
        budget.year = 2023
        budget.month = 10
        budget.workspace_id = uuid4()
        budget.owner_id = uuid4()
        budget.category_id = uuid4()
        budget.created_at = datetime.now()
        budget.updated_at = datetime.now()
        
        # Returns list of tuples (budget, spent, progress)
        mock_instance.execute = AsyncMock(return_value=([(budget, 100.0, 10.0)], 1))

        response = await client.get(f"/budgets?workspace_id={workspace_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["spent_amount"] == 100.0

@pytest.mark.asyncio
async def test_update_budget_success(client):
    budget_id = str(uuid4())
    payload = {"limit_amount": 2000.0}
    
    with patch("src.api.routes.budget.UpdateBudget") as MockUseClass:
        mock_instance = MockUseClass.return_value
        budget = MagicMock(spec=Budget)
        budget.id = budget_id
        budget.limit_amount = 2000.0
        budget.year = 2023
        budget.month = 10
        budget.workspace_id = uuid4()
        budget.owner_id = uuid4()
        budget.category_id = uuid4()
        budget.created_at = datetime.now()
        budget.updated_at = datetime.now()
        
        mock_instance.execute = AsyncMock(return_value=(budget, 0.0, 0.0))

        response = await client.put(f"/budgets/{budget_id}", json=payload)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["limit_amount"] == 2000.0

@pytest.mark.asyncio
async def test_delete_budget_success(client):
    budget_id = str(uuid4())
    
    with patch("src.api.routes.budget.DeleteBudget") as MockUseClass:
        mock_instance = MockUseClass.return_value
        mock_instance.execute = AsyncMock(return_value=None)

        response = await client.delete(f"/budgets/{budget_id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.asyncio
async def test_list_categories(client, mock_category_repo):
    workspace_id = str(uuid4())
    
    category = MagicMock()
    category.id = uuid4()
    category.name = "Test Category"
    category.description = "Test Description" # Added missing field
    category.is_default = False
    category.workspace_id = uuid4() # Added missing field
    
    # We also need to mock workspace_repo for access check
    # But checking source code:
    # 87:         if workspace_id:
    # 89:             member = await workspace_repo.get_member(workspace_id, current_user.id)
    # ...
    # 95:             categories = await category_repo.list_by_workspace(workspace_id)
    
    # Since we mocked all repos, we need to mock workspace_repo behavior in this test or rely on default AsyncMock?
    # default AsyncMock returns AsyncMock, which is truthy.
    
    # BUT, we need to mock list_by_workspace return value.
    mock_category_repo.list_by_workspace.return_value = [category]
    # And mock workspace repo get member to return something truthy to pass access check.
    # We should access mock_workspace_repo from client fixture? 
    # Yes, we requested mock_workspace_repo in this test signature, so we can configure it.
    
    response = await client.get(f"/budgets/categories?workspace_id={workspace_id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Category"

@pytest.mark.asyncio
async def test_internal_server_error(client):
    # Pass arbitrary error
    payload = {
        "workspace_id": str(uuid4()),
        "category_id": str(uuid4()),
        "limit_amount": 1000.0,
        "month": 10,
        "year": 2023
    }
    
    with patch("src.api.routes.budget.CreateBudget") as MockUseClass:
        mock_instance = MockUseClass.return_value
        mock_instance.execute = AsyncMock(side_effect=Exception("Unexpected"))

        response = await client.post("/budgets", json=payload)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

@pytest.mark.asyncio
async def test_list_categories_defaults(client, mock_category_repo):
    category = MagicMock()
    category.id = uuid4()
    category.name = "Default Category"
    category.description = "Desc"
    category.is_default = True
    category.workspace_id = None
    
    mock_category_repo.list_defaults.return_value = [category]
    
    response = await client.get("/budgets/categories")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["is_default"] is True
    assert mock_category_repo.list_defaults.called

@pytest.mark.asyncio
async def test_list_categories_unauthorized(client, mock_category_repo, mock_workspace_repo):
    workspace_id = str(uuid4())
    # Mock workspace check failure
    mock_workspace_repo.get_member.return_value = None
    mock_workspace_repo.get_by_id.return_value = MagicMock(owner_id=uuid4()) # Not current user
    
    response = await client.get(f"/budgets/categories?workspace_id={workspace_id}")
    
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_get_budget_unauthorized(client):
    budget_id = str(uuid4())
    with patch("src.api.routes.budget.GetBudget") as MockUseClass:
        mock_instance = MockUseClass.return_value
        mock_instance.execute = AsyncMock(side_effect=UnauthorizedError("Access denied"))
        
        response = await client.get(f"/budgets/{budget_id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_list_budgets_unauthorized(client):
    workspace_id = str(uuid4())
    with patch("src.api.routes.budget.ListBudgets") as MockUseClass:
        mock_instance = MockUseClass.return_value
        mock_instance.execute = AsyncMock(side_effect=UnauthorizedError("Access denied"))
        
        response = await client.get(f"/budgets?workspace_id={workspace_id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_update_budget_errors(client):
    budget_id = str(uuid4())
    payload = {"limit_amount": 2000.0}
    
    with patch("src.api.routes.budget.UpdateBudget") as MockUseClass:
        mock_instance = MockUseClass.return_value
        
        # Not Found
        mock_instance.execute = AsyncMock(side_effect=NotFoundError("Not found"))
        response = await client.put(f"/budgets/{budget_id}", json=payload)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Unauthorized
        mock_instance.execute = AsyncMock(side_effect=UnauthorizedError("Denied"))
        response = await client.put(f"/budgets/{budget_id}", json=payload)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Validation Error
        mock_instance.execute = AsyncMock(side_effect=ValidationError("Invalid"))
        response = await client.put(f"/budgets/{budget_id}", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_delete_budget_errors(client):
    budget_id = str(uuid4())
    
    with patch("src.api.routes.budget.DeleteBudget") as MockUseClass:
        mock_instance = MockUseClass.return_value
        
        # Not Found
        mock_instance.execute = AsyncMock(side_effect=NotFoundError("Not found"))
        response = await client.delete(f"/budgets/{budget_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Unauthorized
        mock_instance.execute = AsyncMock(side_effect=UnauthorizedError("Denied"))
        response = await client.delete(f"/budgets/{budget_id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_internal_server_errors_all_routes(client):
    budget_id = str(uuid4())
    payload = {"limit_amount": 2000.0}
    workspace_id = str(uuid4())
    
    # Get Budget
    with patch("src.api.routes.budget.GetBudget") as MockUseClass:
        mock_instance = MockUseClass.return_value
        mock_instance.execute = AsyncMock(side_effect=Exception("Unexpected"))
        response = await client.get(f"/budgets/{budget_id}")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    # List Budgets
    with patch("src.api.routes.budget.ListBudgets") as MockUseClass:
        mock_instance = MockUseClass.return_value
        mock_instance.execute = AsyncMock(side_effect=Exception("Unexpected"))
        response = await client.get(f"/budgets?workspace_id={workspace_id}")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    # Update Budget
    with patch("src.api.routes.budget.UpdateBudget") as MockUseClass:
        mock_instance = MockUseClass.return_value
        mock_instance.execute = AsyncMock(side_effect=Exception("Unexpected"))
        response = await client.put(f"/budgets/{budget_id}", json=payload)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    # Delete Budget
    with patch("src.api.routes.budget.DeleteBudget") as MockUseClass:
        mock_instance = MockUseClass.return_value
        mock_instance.execute = AsyncMock(side_effect=Exception("Unexpected"))
        response = await client.delete(f"/budgets/{budget_id}")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

@pytest.mark.asyncio
async def test_list_categories_internal_error(client, mock_category_repo):
    mock_category_repo.list_defaults.side_effect = Exception("Repo fail")
    response = await client.get("/budgets/categories")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
