import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from src.application.use_cases.budget.create.index import CreateBudget
from src.application.use_cases.budget.create.dtos import CreateBudgetRequestDto
from src.application.use_cases.budget.update.index import UpdateBudget
from src.application.use_cases.budget.delete.index import DeleteBudget
from src.application.use_cases.budget.get.index import GetBudget
from src.application.use_cases.budget.list.index import ListBudgets
from src.domain.errors import NotFoundError, UnauthorizedError, ConflictError
from src.domain.workspace.value_objects import WorkspaceRole
from src.domain.budget.models import Budget

@pytest.fixture
def mock_budget_repo():
    return AsyncMock()

@pytest.fixture
def mock_workspace_repo():
    return AsyncMock()

@pytest.fixture
def mock_category_repo():
    return AsyncMock()

@pytest.fixture
def mock_movement_service():
    return AsyncMock()

@pytest.fixture
def user():
    user = MagicMock()
    user.id = uuid4()
    return user

@pytest.fixture
def workspace_id():
    return uuid4()

@pytest.fixture
def category_id():
    return uuid4()

@pytest.mark.asyncio
class TestCreateBudget:
    async def test_create_budget_success(self, mock_budget_repo, mock_workspace_repo, mock_category_repo, user, workspace_id, category_id):
        use_case = CreateBudget(mock_budget_repo, mock_workspace_repo, mock_category_repo)
        
        dto = CreateBudgetRequestDto(
            workspace_id=workspace_id,
            category_id=category_id,
            limit_amount=1000.0,
            month=10,
            year=2023
        )

        mock_workspace_repo.get_member.return_value = MagicMock(role=WorkspaceRole.OWNER)
        
        category = MagicMock()
        category.is_default = False
        category.workspace_id = workspace_id
        mock_category_repo.get_by_id.return_value = category
        
        mock_budget_repo.get_by_category_period.return_value = None

        budget = await use_case.execute(user, dto)

        assert budget.limit_amount == 1000.0
        mock_budget_repo.add.assert_called_once()

    async def test_create_budget_unauthorized_workspace(self, mock_budget_repo, mock_workspace_repo, mock_category_repo, user, workspace_id, category_id):
        use_case = CreateBudget(mock_budget_repo, mock_workspace_repo, mock_category_repo)
        dto = CreateBudgetRequestDto(workspace_id=workspace_id, category_id=category_id, limit_amount=100, month=1, year=2023)
        
        mock_workspace_repo.get_member.return_value = None
        mock_workspace_repo.get_by_id.return_value = MagicMock(owner_id=uuid4()) # Not owner

        with pytest.raises(UnauthorizedError):
            await use_case.execute(user, dto)

    async def test_create_budget_category_not_found(self, mock_budget_repo, mock_workspace_repo, mock_category_repo, user, workspace_id, category_id):
        use_case = CreateBudget(mock_budget_repo, mock_workspace_repo, mock_category_repo)
        dto = CreateBudgetRequestDto(workspace_id=workspace_id, category_id=category_id, limit_amount=100, month=1, year=2023)
        
        mock_workspace_repo.get_member.return_value = MagicMock()
        mock_category_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError):
            await use_case.execute(user, dto)

    async def test_create_budget_category_wrong_workspace(self, mock_budget_repo, mock_workspace_repo, mock_category_repo, user, workspace_id, category_id):
        use_case = CreateBudget(mock_budget_repo, mock_workspace_repo, mock_category_repo)
        dto = CreateBudgetRequestDto(workspace_id=workspace_id, category_id=category_id, limit_amount=100, month=1, year=2023)
        
        mock_workspace_repo.get_member.return_value = MagicMock()
        category = MagicMock()
        category.is_default = False
        category.workspace_id = uuid4() # Different workspace
        mock_category_repo.get_by_id.return_value = category

        with pytest.raises(UnauthorizedError):
            await use_case.execute(user, dto)

    async def test_create_budget_conflict(self, mock_budget_repo, mock_workspace_repo, mock_category_repo, user, workspace_id, category_id):
        use_case = CreateBudget(mock_budget_repo, mock_workspace_repo, mock_category_repo)
        dto = CreateBudgetRequestDto(workspace_id=workspace_id, category_id=category_id, limit_amount=100, month=1, year=2023)
        
        mock_workspace_repo.get_member.return_value = MagicMock()
        category = MagicMock()
        category.is_default = True
        mock_category_repo.get_by_id.return_value = category
        
        mock_budget_repo.get_by_category_period.return_value = MagicMock() # Exists

        with pytest.raises(ConflictError):
            await use_case.execute(user, dto)


@pytest.mark.asyncio
class TestUpdateBudget:
    async def test_update_budget_success(self, mock_budget_repo, mock_workspace_repo, mock_movement_service, user, workspace_id):
        use_case = UpdateBudget(mock_budget_repo, mock_workspace_repo, mock_movement_service)
        budget = MagicMock(spec=Budget)
        budget.workspace_id = workspace_id
        budget.limit_amount = 500.0
        mock_budget_repo.get_by_id.return_value = budget
        
        mock_workspace_repo.get_member.return_value = MagicMock(role=WorkspaceRole.EDITOR)
        mock_movement_service.get_spent_amount.return_value = 250.0

        budget.update_limit.side_effect = lambda amount: setattr(budget, 'limit_amount', amount)

        updated, spent, progress = await use_case.execute(uuid4(), user, 1000.0)

        assert budget.update_limit.called
        mock_budget_repo.update.assert_called_once()
        assert spent == 250.0
        assert progress == 25.0

    async def test_update_budget_not_found(self, mock_budget_repo, mock_workspace_repo, mock_movement_service, user):
        use_case = UpdateBudget(mock_budget_repo, mock_workspace_repo, mock_movement_service)
        mock_budget_repo.get_by_id.return_value = None
        
        with pytest.raises(NotFoundError):
            await use_case.execute(uuid4(), user, 100)

    async def test_update_budget_unauthorized_role(self, mock_budget_repo, mock_workspace_repo, mock_movement_service, user, workspace_id):
        use_case = UpdateBudget(mock_budget_repo, mock_workspace_repo, mock_movement_service)
        budget = MagicMock(workspace_id=workspace_id)
        mock_budget_repo.get_by_id.return_value = budget
        
        mock_workspace_repo.get_member.return_value = MagicMock(role='VIEWER') # Not editor/owner

        with pytest.raises(UnauthorizedError):
            await use_case.execute(uuid4(), user, 100)

@pytest.mark.asyncio
class TestDeleteBudget:
    async def test_delete_budget_success_owner(self, mock_budget_repo, mock_workspace_repo, user, workspace_id):
        use_case = DeleteBudget(mock_budget_repo, mock_workspace_repo)
        budget = MagicMock(spec=Budget)
        budget.workspace_id = workspace_id
        mock_budget_repo.get_by_id.return_value = budget
        
        mock_workspace_repo.get_member.return_value = None # Not a member, check if owner
        workspace = MagicMock(owner_id=user.id)
        mock_workspace_repo.get_by_id.return_value = workspace

        await use_case.execute(uuid4(), user)

        assert budget.delete.called
        mock_budget_repo.remove.assert_called_once()

    async def test_delete_budget_unauthorized(self, mock_budget_repo, mock_workspace_repo, user, workspace_id):
        use_case = DeleteBudget(mock_budget_repo, mock_workspace_repo)
        budget = MagicMock(workspace_id=workspace_id)
        mock_budget_repo.get_by_id.return_value = budget
        
        mock_workspace_repo.get_member.return_value = MagicMock(role='VIEWER')

        with pytest.raises(UnauthorizedError):
            await use_case.execute(uuid4(), user)


@pytest.mark.asyncio
class TestGetBudget:
    async def test_get_budget_success(self, mock_budget_repo, mock_workspace_repo, mock_movement_service, user, workspace_id):
        use_case = GetBudget(mock_budget_repo, mock_workspace_repo, mock_movement_service)
        budget = MagicMock(workspace_id=workspace_id, limit_amount=100.0)
        mock_budget_repo.get_by_id.return_value = budget
        
        mock_workspace_repo.get_member.return_value = MagicMock()
        mock_movement_service.get_spent_amount.return_value = 50.0

        res_budget, spent, progress = await use_case.execute(uuid4(), user)

        assert res_budget == budget
        assert spent == 50.0
        assert progress == 50.0

    async def test_get_budget_zero_limit(self, mock_budget_repo, mock_workspace_repo, mock_movement_service, user, workspace_id):
        use_case = GetBudget(mock_budget_repo, mock_workspace_repo, mock_movement_service)
        budget = MagicMock(workspace_id=workspace_id, limit_amount=0.0)
        mock_budget_repo.get_by_id.return_value = budget
        
        mock_workspace_repo.get_member.return_value = MagicMock()
        mock_movement_service.get_spent_amount.return_value = 10.0

        _, _, progress = await use_case.execute(uuid4(), user)
        assert progress == 0

    async def test_get_budget_not_found(self, mock_budget_repo, mock_workspace_repo, mock_movement_service, user):
        use_case = GetBudget(mock_budget_repo, mock_workspace_repo, mock_movement_service)
        mock_budget_repo.get_by_id.return_value = None
        
        with pytest.raises(NotFoundError):
            await use_case.execute(uuid4(), user)

    async def test_get_budget_unauthorized(self, mock_budget_repo, mock_workspace_repo, mock_movement_service, user, workspace_id):
        use_case = GetBudget(mock_budget_repo, mock_workspace_repo, mock_movement_service)
        budget = MagicMock(workspace_id=workspace_id)
        mock_budget_repo.get_by_id.return_value = budget
        
        mock_workspace_repo.get_member.return_value = None
        workspace = MagicMock(owner_id=uuid4()) # Not owner
        mock_workspace_repo.get_by_id.return_value = workspace

        with pytest.raises(UnauthorizedError):
            await use_case.execute(uuid4(), user)

@pytest.mark.asyncio
class TestListBudgets:
    async def test_list_budgets_success(self, mock_budget_repo, mock_workspace_repo, mock_movement_service, user, workspace_id):
        use_case = ListBudgets(mock_budget_repo, mock_workspace_repo, mock_movement_service)
        
        mock_workspace_repo.get_member.return_value = MagicMock()
        
        budget1 = MagicMock(limit_amount=100.0)
        budget2 = MagicMock(limit_amount=200.0)
        mock_budget_repo.list_by_workspace.return_value = ([budget1, budget2], 2)
        mock_movement_service.get_spent_amount.side_effect = [50.0, 20.0]

        results, total = await use_case.execute(user, workspace_id)

        assert total == 2
        assert len(results) == 2
        assert results[0][1] == 50.0 # spent 1

    async def test_list_budgets_unauthorized(self, mock_budget_repo, mock_workspace_repo, mock_movement_service, user, workspace_id):
        use_case = ListBudgets(mock_budget_repo, mock_workspace_repo, mock_movement_service)
        
        mock_workspace_repo.get_member.return_value = None
        workspace = MagicMock(owner_id=uuid4()) # Not owner
        mock_workspace_repo.get_by_id.return_value = workspace
        
        with pytest.raises(UnauthorizedError):
            await use_case.execute(user, workspace_id)
