from src.domain.budget.models import Budget
from src.infrastructure.budget.models import BudgetORM


class BudgetMapper:
    @staticmethod
    def to_domain(orm: BudgetORM) -> Budget:
        return Budget(
            id=orm.id,
            workspace_id=orm.workspace_id,
            owner_id=orm.owner_id,
            category_id=orm.category_id,
            limit_amount=orm.limit_amount,
            month=orm.month,
            year=orm.year,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )

    @staticmethod
    def to_orm(domain: Budget) -> BudgetORM:
        return BudgetORM(
            id=domain.id,
            workspace_id=domain.workspace_id,
            owner_id=domain.owner_id,
            category_id=domain.category_id,
            limit_amount=domain.limit_amount,
            month=domain.month,
            year=domain.year,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
            deleted_at=domain.deleted_at,
        )
