from typing import List, Optional, Tuple
from uuid import UUID

from src.application.use_cases.budget.movement_service import MovementService
from src.domain.auth.models import User
from src.domain.budget.models import Budget
from src.domain.budget.repositories import BudgetRepository
from src.domain.errors import UnauthorizedError
from src.domain.workspace.repositories import WorkspaceRepository


class ListBudgets:
    def __init__(
        self,
        budget_repo: BudgetRepository,
        workspace_repo: WorkspaceRepository,
        movement_service: MovementService,
    ):
        self._budget_repo = budget_repo
        self._workspace_repo = workspace_repo
        self._movement_service = movement_service

    async def execute(
        self,
        user: User,
        workspace_id: UUID,
        category_id: Optional[UUID] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[Tuple[Budget, float, float]], int]:
        member = await self._workspace_repo.get_member(workspace_id, user.id)
        if not member:
            workspace = await self._workspace_repo.get_by_id(workspace_id)
            if not workspace or workspace.owner_id != user.id:
                raise UnauthorizedError("You do not have access to this workspace")

        offset = (page - 1) * size
        budgets, total = await self._budget_repo.list_by_workspace(
            workspace_id, category_id, month, year, size, offset
        )

        results = []
        for budget in budgets:
            spent = await self._movement_service.get_spent_amount(
                budget.workspace_id, budget.category_id, budget.month, budget.year
            )
            progress = (
                (spent / budget.limit_amount) * 100 if budget.limit_amount > 0 else 0
            )
            results.append((budget, spent, round(progress, 2)))

        return results, total
