import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.budget.repositories import SQLBudgetRepository, SQLCategoryRepository
from src.infrastructure.workspace.repositories import SQLWorkspaceRepository
from src.infrastructure.auth.repositories import SQLUserRepository
from src.domain.budget.models import Budget, Category
from src.domain.workspace.models import Workspace
from src.domain.auth.models import User
from src.domain.auth.value_objects import Email

@pytest.mark.asyncio
async def test_budget_repository_flow(db_session: AsyncSession):
    budget_repo = SQLBudgetRepository(db_session)
    category_repo = SQLCategoryRepository(db_session)
    workspace_repo = SQLWorkspaceRepository(db_session)
    user_repo = SQLUserRepository(db_session)

    # 1. Setup user and workspace
    user = User(email=Email("budget_test@example.com"), password_hash="hash", full_name="Budget Tester")
    await user_repo.add(user)
    await db_session.commit()

    workspace = Workspace(name="Finance", owner_id=user.id)
    await workspace_repo.add(workspace)
    await db_session.commit()

    # 1.1 Add Category
    category = Category(name="Groceries", is_default=True)
    await category_repo.add(category)
    await db_session.commit()

    # 2. Add budget
    budget = Budget(
        workspace_id=workspace.id,
        owner_id=user.id,
        category_id=category.id,
        limit_amount=300.0,
        month=2,
        year=2024
    )
    await budget_repo.add(budget)
    await db_session.commit()

    # 3. Get by id
    found = await budget_repo.get_by_id(budget.id)
    assert found is not None
    assert found.category_id == category.id
    assert found.limit_amount == 300.0

    # 4. Get by category and period
    found_period = await budget_repo.get_by_category_period(
        workspace.id, category.id, 2, 2024
    )
    assert found_period is not None
    assert found_period.id == budget.id

    # 5. List budgets
    items, total = await budget_repo.list_by_workspace(workspace.id)
    assert total == 1
    assert items[0].id == budget.id

    # 6. Update budget
    budget.update_limit(400.0)
    await budget_repo.update(budget)
    await db_session.commit()

    updated = await budget_repo.get_by_id(budget.id)
    assert updated.limit_amount == 400.0

    # 7. Soft remove budget
    budget.delete()
    await budget_repo.remove(budget)
    await db_session.commit()

    assert await budget_repo.get_by_id(budget.id) is None
    
    # Verify it still exists in DB but not returned by repository
    items, total = await budget_repo.list_by_workspace(workspace.id)
    assert total == 0
