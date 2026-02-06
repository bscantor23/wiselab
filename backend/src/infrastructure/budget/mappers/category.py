from src.domain.budget.models import Category
from src.infrastructure.budget.models.category import CategoryORM


class CategoryMapper:
    @staticmethod
    def to_domain(orm: CategoryORM) -> Category:
        return Category(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            is_default=orm.is_default,
            workspace_id=orm.workspace_id,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    @staticmethod
    def to_orm(domain: Category) -> CategoryORM:
        return CategoryORM(
            id=domain.id,
            name=domain.name,
            description=domain.description,
            is_default=domain.is_default,
            workspace_id=domain.workspace_id,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )
