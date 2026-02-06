from uuid import UUID

from src.domain.auth.models import User
from src.domain.budget.repositories import BudgetRepository
from src.domain.errors import NotFoundError, UnauthorizedError
from src.domain.workspace.repositories import WorkspaceRepository
from src.domain.workspace.value_objects import WorkspaceRole


class DeleteBudget:
    def __init__(
        self, budget_repo: BudgetRepository, workspace_repo: WorkspaceRepository
    ):
        self._budget_repo = budget_repo
        self._workspace_repo = workspace_repo

    async def execute(self, budget_id: UUID, user: User) -> None:
        budget = await self._budget_repo.get_by_id(budget_id)
        if not budget:
            raise NotFoundError("Budget not found")

        member = await self._workspace_repo.get_member(budget.workspace_id, user.id)
        is_owner = False
        if not member:
            workspace = await self._workspace_repo.get_by_id(budget.workspace_id)
            if not workspace or workspace.owner_id != user.id:
                raise UnauthorizedError("You do not have access to this workspace")
            is_owner = True

        if not is_owner and member.role not in [
            WorkspaceRole.OWNER,
            WorkspaceRole.EDITOR,
        ]:
            raise UnauthorizedError("Only editors or owners can delete budgets")

        budget.delete()
        await self._budget_repo.remove(budget)
