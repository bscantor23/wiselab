from typing import List, Optional
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.workspace.models import Workspace, WorkspaceMember
from src.domain.workspace.repositories import WorkspaceRepository
from src.domain.workspace.value_objects import WorkspaceRole
from src.infrastructure.workspace.mappers import WorkspaceMapper, WorkspaceMemberMapper
from src.infrastructure.workspace.models import WorkspaceMemberORM, WorkspaceORM


class SQLWorkspaceRepository(WorkspaceRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, workspace: Workspace) -> None:
        orm_workspace = WorkspaceMapper.to_orm(workspace)
        self._session.add(orm_workspace)

    async def get_by_id(self, id: UUID) -> Optional[Workspace]:
        result = await self._session.execute(select(WorkspaceORM).filter_by(id=id))
        orm_workspace = result.scalar_one_or_none()
        if not orm_workspace:
            return None
        return WorkspaceMapper.to_domain(orm_workspace)

    async def list_by_user(self, user_id: UUID) -> List[Workspace]:
        # User is either owner or member
        stmt = (
            select(WorkspaceORM)
            .join(
                WorkspaceMemberORM,
                WorkspaceORM.id == WorkspaceMemberORM.workspace_id,
                isouter=True,
            )
            .where(
                (WorkspaceORM.owner_id == user_id)
                | (WorkspaceMemberORM.user_id == user_id)
            )
            .distinct()
        )

        result = await self._session.execute(stmt)

        return [WorkspaceMapper.to_domain(orm) for orm in result.scalars()]

    async def get_by_name_and_owner(
        self, name: str, owner_id: UUID
    ) -> Optional[Workspace]:
        stmt = select(WorkspaceORM).filter_by(name=name, owner_id=owner_id)
        result = await self._session.execute(stmt)
        orm_workspace = result.scalar_one_or_none()
        if not orm_workspace:
            return None
        return WorkspaceMapper.to_domain(orm_workspace)

    async def add_member(self, member: WorkspaceMember) -> None:
        orm_member = WorkspaceMemberMapper.to_orm(member)
        self._session.add(orm_member)

    async def get_member(
        self, workspace_id: UUID, user_id: UUID
    ) -> Optional[WorkspaceMember]:
        # First check if the user is the workspace owner
        workspace_stmt = select(WorkspaceORM).filter_by(id=workspace_id)
        workspace_result = await self._session.execute(workspace_stmt)
        workspace_orm = workspace_result.scalar_one_or_none()

        if workspace_orm and workspace_orm.owner_id == user_id:
            # Owner is not in workspace_members table, create synthetic member
            return WorkspaceMember(
                workspace_id=workspace_id,
                user_id=user_id,
                role=WorkspaceRole.OWNER,
                joined_at=workspace_orm.created_at,
                id=None,  # Synthetic member has no ID
            )

        # Check regular members table
        stmt = select(WorkspaceMemberORM).filter_by(
            workspace_id=workspace_id, user_id=user_id
        )
        result = await self._session.execute(stmt)
        orm_member = result.scalar_one_or_none()
        if not orm_member:
            return None
        return WorkspaceMemberMapper.to_domain(orm_member)

    async def list_members(self, workspace_id: UUID) -> List[WorkspaceMember]:
        # Get the workspace to access owner_id
        workspace_stmt = select(WorkspaceORM).filter_by(id=workspace_id)
        workspace_result = await self._session.execute(workspace_stmt)
        workspace_orm = workspace_result.scalar_one_or_none()

        members = []

        # Add owner as first member if workspace exists
        if workspace_orm:
            owner_member = WorkspaceMember(
                workspace_id=workspace_id,
                user_id=workspace_orm.owner_id,
                role=WorkspaceRole.OWNER,
                joined_at=workspace_orm.created_at,
                id=None,  # Synthetic member has no ID
            )
            members.append(owner_member)

        # Get regular members from workspace_members table (exclude owner if already present)
        stmt = select(WorkspaceMemberORM).filter(
            WorkspaceMemberORM.workspace_id == workspace_id,
            (
                WorkspaceMemberORM.user_id != workspace_orm.owner_id
                if workspace_orm
                else True
            ),
        )
        result = await self._session.execute(stmt)
        members.extend([WorkspaceMemberMapper.to_domain(m) for m in result.scalars()])

        return members

    async def update_member(self, member: WorkspaceMember) -> None:
        stmt = (
            update(WorkspaceMemberORM)
            .where(WorkspaceMemberORM.id == member.id)
            .values(role=member.role.value)
        )
        await self._session.execute(stmt)

    async def remove_member(self, workspace_id: UUID, user_id: UUID) -> None:
        stmt = delete(WorkspaceMemberORM).where(
            WorkspaceMemberORM.workspace_id == workspace_id,
            WorkspaceMemberORM.user_id == user_id,
        )
        await self._session.execute(stmt)

    async def update(self, workspace: Workspace) -> None:
        stmt = (
            update(WorkspaceORM)
            .where(WorkspaceORM.id == workspace.id)
            .values(
                name=workspace.name,
                description=workspace.description,
                category=workspace.category,
                is_active=workspace.is_active,
                updated_at=workspace.updated_at,
            )
        )
        await self._session.execute(stmt)

    async def remove(self, workspace: Workspace) -> None:
        """Deletes a workspace permanently. Consider soft-delete in future."""
        stmt = delete(WorkspaceORM).where(WorkspaceORM.id == workspace.id)
        await self._session.execute(stmt)

    async def list(self) -> List[Workspace]:
        """List all workspaces (Administrative use)."""
        result = await self._session.execute(select(WorkspaceORM))
        return [WorkspaceMapper.to_domain(orm) for orm in result.scalars()]
