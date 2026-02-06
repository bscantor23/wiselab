from uuid import UUID

from src.application.use_cases.budget.movement_service import MovementService
from src.domain.auth.models import User
from src.domain.budget.models import Budget
from src.domain.budget.repositories import BudgetRepository
from src.domain.errors import NotFoundError, UnauthorizedError
from src.domain.workspace.repositories import WorkspaceRepository


class GetBudget:
    def __init__(
        self,
        budget_repo: BudgetRepository,
        workspace_repo: WorkspaceRepository,
        movement_service: MovementService,
    ):
        self._budget_repo = budget_repo
        self._workspace_repo = workspace_repo
        self._movement_service = movement_service

    async def execute(self, budget_id: UUID, user: User) -> tuple[Budget, float, float]:
        budget = await self._budget_repo.get_by_id(budget_id)
        if not budget:
            raise NotFoundError("Budget not found")

        member = await self._workspace_repo.get_member(budget.workspace_id, user.id)
        if not member:
            workspace = await self._workspace_repo.get_by_id(budget.workspace_id)
            if not workspace or workspace.owner_id != user.id:
                raise UnauthorizedError(
                    "You do not have access to this budget's workspace"
                )

        spent_amount = await self._movement_service.get_spent_amount(
            budget.workspace_id, budget.category_id, budget.month, budget.year
        )

        progress = (
            (spent_amount / budget.limit_amount) * 100 if budget.limit_amount > 0 else 0
        )

        return budget, spent_amount, round(progress, 2)
