from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.repository import Repository
from src.domain.workspace.models import Workspace, WorkspaceMember


class WorkspaceRepository(Repository, ABC):
    @abstractmethod
    async def add(self, workspace: Workspace) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Workspace]:
        pass

    @abstractmethod
    async def list_by_user(self, user_id: UUID) -> List[Workspace]:
        pass

    @abstractmethod
    async def get_by_name_and_owner(self, name: str, owner_id: UUID) -> Optional[Workspace]:
        pass

    @abstractmethod
    async def update(self, workspace: Workspace) -> None:
        pass

    @abstractmethod
    async def remove(self, workspace: Workspace) -> None:
        pass

    @abstractmethod
    async def add_member(self, member: WorkspaceMember) -> None:
        pass

    @abstractmethod
    async def get_member(
        self, workspace_id: UUID, user_id: UUID
    ) -> Optional[WorkspaceMember]:
        pass

    @abstractmethod
    async def list_members(self, workspace_id: UUID) -> List[WorkspaceMember]:
        pass

    @abstractmethod
    async def update_member(self, member: WorkspaceMember) -> None:
        pass

    @abstractmethod
    async def remove_member(self, workspace_id: UUID, user_id: UUID) -> None:
        pass
