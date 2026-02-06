import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.dependencies.auth import get_current_user
from src.api.dependencies.budget import (
    get_budget_repository,
    get_category_repository,
    get_movement_service,
)
from src.api.dependencies.workspace import get_workspace_repository
from src.infrastructure.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.use_cases.budget.create.dtos import (
    BudgetResponseDto,
    CategoryResponseDto,
    CreateBudgetRequestDto,
)
from src.application.use_cases.budget.create.index import CreateBudget
from src.application.use_cases.budget.delete.index import DeleteBudget
from src.application.use_cases.budget.get.index import GetBudget
from src.application.use_cases.budget.list.dtos import ListBudgetsResponseDto
from src.application.use_cases.budget.list.index import ListBudgets
from src.application.use_cases.budget.update.dtos import UpdateBudgetRequestDto
from src.application.use_cases.budget.update.index import UpdateBudget
from src.domain.auth.models import User
from src.domain.errors import (
    ConflictError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)

router = APIRouter(prefix="/budgets", tags=["budgets"])
logger = logging.getLogger(__name__)


@router.post("", response_model=BudgetResponseDto, status_code=status.HTTP_201_CREATED)
async def create_budget(
    data: CreateBudgetRequestDto,
    current_user: User = Depends(get_current_user),
    budget_repo=Depends(get_budget_repository),
    category_repo=Depends(get_category_repository),
    workspace_repo=Depends(get_workspace_repository),
    session: AsyncSession = Depends(get_db),
):
    try:
        use_case = CreateBudget(budget_repo, workspace_repo, category_repo)
        budget = await use_case.execute(current_user, data)
        await session.commit()
        return {
            "id": budget.id,
            "workspace_id": budget.workspace_id,
            "owner_id": budget.owner_id,
            "category_id": budget.category_id,
            "limit_amount": budget.limit_amount,
            "month": budget.month,
            "year": budget.year,
            "created_at": budget.created_at,
            "updated_at": budget.updated_at,
        }
    except UnauthorizedError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except (ValidationError, ConflictError) as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating budget: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/categories", response_model=list[CategoryResponseDto])
async def list_categories(
    workspace_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    category_repo=Depends(get_category_repository),
    workspace_repo=Depends(get_workspace_repository),
):
    try:
        if workspace_id:
            # Validate workspace access
            member = await workspace_repo.get_member(workspace_id, current_user.id)
            if not member:
                workspace = await workspace_repo.get_by_id(workspace_id)
                if not workspace or workspace.owner_id != current_user.id:
                    raise UnauthorizedError("You do not have access to this workspace")
            
            categories = await category_repo.list_by_workspace(workspace_id)
        else:
            categories = await category_repo.list_defaults()
            
        return [
            CategoryResponseDto(
                id=c.id,
                name=c.name,
                description=c.description,
                is_default=c.is_default,
                workspace_id=c.workspace_id,
            )
            for c in categories
        ]
    except UnauthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/{id}", response_model=BudgetResponseDto)
async def get_budget(
    id: UUID,
    current_user: User = Depends(get_current_user),
    budget_repo=Depends(get_budget_repository),
    workspace_repo=Depends(get_workspace_repository),
    movement_service=Depends(get_movement_service),
):
    try:
        use_case = GetBudget(budget_repo, workspace_repo, movement_service)
        budget, spent, progress = await use_case.execute(id, current_user)

        # Map to DTO
        return {
            "id": budget.id,
            "workspace_id": budget.workspace_id,
            "owner_id": budget.owner_id,
            "category_id": budget.category_id,
            "limit_amount": budget.limit_amount,
            "month": budget.month,
            "year": budget.year,
            "spent_amount": spent,
            "progress_percentage": progress,
            "created_at": budget.created_at,
            "updated_at": budget.updated_at,
        }
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UnauthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting budget: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("", response_model=ListBudgetsResponseDto)
async def list_budgets(
    workspace_id: UUID = Query(...),
    category_id: Optional[UUID] = Query(None),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    budget_repo=Depends(get_budget_repository),
    workspace_repo=Depends(get_workspace_repository),
    movement_service=Depends(get_movement_service),
):
    try:
        use_case = ListBudgets(budget_repo, workspace_repo, movement_service)
        results, total = await use_case.execute(
            current_user, workspace_id, category_id, month, year, page, size
        )

        items = []
        for budget, spent, progress in results:
            items.append(
                {
                    "id": budget.id,
                    "workspace_id": budget.workspace_id,
                    "owner_id": budget.owner_id,
                    "category_id": budget.category_id,
                    "limit_amount": budget.limit_amount,
                    "month": budget.month,
                    "year": budget.year,
                    "spent_amount": spent,
                    "progress_percentage": progress,
                    "created_at": budget.created_at,
                    "updated_at": budget.updated_at,
                }
            )

        return {"items": items, "total": total, "page": page, "size": size}
    except UnauthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing budgets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("/{id}", response_model=BudgetResponseDto)
async def update_budget(
    id: UUID,
    data: UpdateBudgetRequestDto,
    current_user: User = Depends(get_current_user),
    budget_repo=Depends(get_budget_repository),
    workspace_repo=Depends(get_workspace_repository),
    movement_service=Depends(get_movement_service),
    session: AsyncSession = Depends(get_db),
):
    try:
        use_case = UpdateBudget(budget_repo, workspace_repo, movement_service)
        budget, spent, progress = await use_case.execute(
            id, current_user, data.limit_amount
        )
        await session.commit()

        return {
            "id": budget.id,
            "workspace_id": budget.workspace_id,
            "owner_id": budget.owner_id,
            "category_id": budget.category_id,
            "limit_amount": budget.limit_amount,
            "month": budget.month,
            "year": budget.year,
            "spent_amount": spent,
            "progress_percentage": progress,
            "created_at": budget.created_at,
            "updated_at": budget.updated_at,
        }
    except NotFoundError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UnauthorizedError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValidationError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        await session.rollback()
        logger.error(f"Error updating budget: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    id: UUID,
    current_user: User = Depends(get_current_user),
    budget_repo=Depends(get_budget_repository),
    workspace_repo=Depends(get_workspace_repository),
    session: AsyncSession = Depends(get_db),
):
    try:
        use_case = DeleteBudget(budget_repo, workspace_repo)
        await use_case.execute(id, current_user)
        await session.commit()
    except NotFoundError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UnauthorizedError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        await session.rollback()
        logger.error(f"Error deleting budget: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
