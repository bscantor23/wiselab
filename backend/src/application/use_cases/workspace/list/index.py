from typing import List

from src.domain.auth.models import User
from src.domain.workspace.models import Workspace
from src.domain.workspace.repositories import WorkspaceRepository


class ListWorkspaces:
    def __init__(self, workspace_repo: WorkspaceRepository):
        self._repo = workspace_repo

    async def execute(self, user: User) -> List[Workspace]:
        return await self._repo.list_by_user(user.id)
