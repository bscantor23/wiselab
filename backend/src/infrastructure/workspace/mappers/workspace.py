from src.domain.workspace.models import Workspace, WorkspaceMember
from src.domain.workspace.value_objects import WorkspaceRole
from src.infrastructure.workspace.models import WorkspaceMemberORM, WorkspaceORM


class WorkspaceMapper:
    @staticmethod
    def to_domain(orm: WorkspaceORM) -> Workspace:
        return Workspace(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            category=orm.category,
            owner_id=orm.owner_id,
            is_active=orm.is_active,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    @staticmethod
    def to_orm(domain: Workspace) -> WorkspaceORM:
        return WorkspaceORM(
            id=domain.id,
            name=domain.name,
            description=domain.description,
            category=domain.category,
            owner_id=domain.owner_id,
            is_active=domain.is_active,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )


class WorkspaceMemberMapper:
    @staticmethod
    def to_domain(orm: WorkspaceMemberORM) -> WorkspaceMember:
        return WorkspaceMember(
            id=orm.id,
            workspace_id=orm.workspace_id,
            user_id=orm.user_id,
            role=WorkspaceRole(orm.role),
            joined_at=orm.joined_at,
        )

    @staticmethod
    def to_orm(domain: WorkspaceMember) -> WorkspaceMemberORM:
        return WorkspaceMemberORM(
            id=domain.id,
            workspace_id=domain.workspace_id,
            user_id=domain.user_id,
            role=domain.role.value,
            joined_at=domain.joined_at,
        )
