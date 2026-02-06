from src.application.use_cases.budget.create.dtos import CreateBudgetRequestDto
from src.domain.auth.models import User
from src.domain.budget.models import Budget
from src.domain.budget.repositories import BudgetRepository, CategoryRepository
from src.domain.errors import ConflictError, UnauthorizedError, NotFoundError
from src.domain.workspace.repositories import WorkspaceRepository


class CreateBudget:
    def __init__(
        self, budget_repo: BudgetRepository, workspace_repo: WorkspaceRepository, category_repo: CategoryRepository
    ):
        self._budget_repo = budget_repo
        self._workspace_repo = workspace_repo
        self._category_repo = category_repo

    async def execute(self, user: User, data: CreateBudgetRequestDto) -> Budget:
        member = await self._workspace_repo.get_member(data.workspace_id, user.id)
        if not member:
            workspace = await self._workspace_repo.get_by_id(data.workspace_id)
            if not workspace or workspace.owner_id != user.id:
                raise UnauthorizedError("You do not have access to this workspace")

        category = await self._category_repo.get_by_id(data.category_id)
        if not category:
            raise NotFoundError("Category not found")
        
        if not category.is_default and category.workspace_id != data.workspace_id:
            raise UnauthorizedError("Category does not belong to this workspace")

        existing = await self._budget_repo.get_by_category_period(
            data.workspace_id, data.category_id, data.month, data.year
        )
        if existing:
            raise ConflictError(
                f"A budget for category '{category.name}' already exists for this period"
            )

        budget = Budget(
            workspace_id=data.workspace_id,
            owner_id=user.id,
            category_id=data.category_id,
            limit_amount=data.limit_amount,
            month=data.month,
            year=data.year,
        )

        await self._budget_repo.add(budget)
        return budget
