from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.auth import get_current_user, get_user_repository
from src.api.dependencies.workspace import get_workspace_repository
from src.application.use_cases.workspace.create.dtos import CreateWorkspaceRequestDto
from src.application.use_cases.workspace.create.index import CreateWorkspace
from src.application.use_cases.workspace.delete.index import DeleteWorkspace
from src.application.use_cases.workspace.get.index import GetWorkspace
from src.application.use_cases.workspace.list.index import ListWorkspaces
from src.application.use_cases.workspace.members.invite.dtos import (
    InviteMemberRequestDto,
)
from src.application.use_cases.workspace.members.invite.index import InviteMember
from src.application.use_cases.workspace.members.list.index import ListMembers
from src.application.use_cases.workspace.members.remove.index import RemoveMember
from src.application.use_cases.workspace.members.update.dtos import (
    UpdateMemberRoleRequestDto,
)
from src.application.use_cases.workspace.members.update.index import UpdateMemberRole
from src.application.use_cases.workspace.shared_dtos import (
    WorkspaceMemberResponseDto,
    WorkspaceResponseDto,
)
from src.application.use_cases.workspace.update.dtos import UpdateWorkspaceRequestDto
from src.application.use_cases.workspace.update.index import UpdateWorkspace
from src.domain.auth.models import User
from src.domain.errors import (
    ConflictError,
    MemberNotFoundError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
    WorkspaceNotFoundError,
)
from src.infrastructure.auth.repositories import SQLUserRepository
from src.infrastructure.database import get_db
from src.infrastructure.workspace.repositories import SQLWorkspaceRepository

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post(
    "", response_model=WorkspaceResponseDto, status_code=status.HTTP_201_CREATED
)
async def create_workspace(
    data: CreateWorkspaceRequestDto,
    current_user: User = Depends(get_current_user),
    repo: SQLWorkspaceRepository = Depends(get_workspace_repository),
    session: AsyncSession = Depends(get_db),
):
    use_case = CreateWorkspace(repo)
    try:
        workspace = await use_case.execute(current_user, data)
        await session.commit()
        return workspace
    except ValidationError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ConflictError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("", response_model=List[WorkspaceResponseDto])
async def list_workspaces(
    current_user: User = Depends(get_current_user),
    repo: SQLWorkspaceRepository = Depends(get_workspace_repository),
):
    use_case = ListWorkspaces(repo)
    try:
        return await use_case.execute(current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{id}", response_model=WorkspaceResponseDto)
async def get_workspace(
    id: UUID,
    current_user: User = Depends(get_current_user),
    repo: SQLWorkspaceRepository = Depends(get_workspace_repository),
):
    use_case = GetWorkspace(repo)
    try:
        return await use_case.execute(id, current_user)
    except WorkspaceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UnauthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/{id}", response_model=WorkspaceResponseDto)
async def update_workspace(
    id: UUID,
    data: UpdateWorkspaceRequestDto,
    current_user: User = Depends(get_current_user),
    repo: SQLWorkspaceRepository = Depends(get_workspace_repository),
    session: AsyncSession = Depends(get_db),
):
    use_case = UpdateWorkspace(repo)
    try:
        workspace = await use_case.execute(id, current_user, data)
        await session.commit()
        return workspace
    except WorkspaceNotFoundError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UnauthorizedError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValidationError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ConflictError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    id: UUID,
    current_user: User = Depends(get_current_user),
    repo: SQLWorkspaceRepository = Depends(get_workspace_repository),
    session: AsyncSession = Depends(get_db),
):
    use_case = DeleteWorkspace(repo)
    try:
        await use_case.execute(id, current_user)
        await session.commit()
    except WorkspaceNotFoundError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UnauthorizedError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except IntegrityError:
        await session.rollback()
        # Foreign key constraint violation - workspace has existing members
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete workspace: The workspace still has associated members. "
            "Please remove all workspace members before attempting to delete the workspace.",
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# Member Management


@router.post(
    "/{id}/members",
    response_model=WorkspaceMemberResponseDto,
    status_code=status.HTTP_201_CREATED,
)
async def invite_member(
    id: UUID,
    data: InviteMemberRequestDto,
    current_user: User = Depends(get_current_user),
    workspace_repo: SQLWorkspaceRepository = Depends(get_workspace_repository),
    user_repo: SQLUserRepository = Depends(get_user_repository),
    session: AsyncSession = Depends(get_db),
):
    use_case = InviteMember(workspace_repo, user_repo)
    try:
        member = await use_case.execute(id, current_user, data)
        await session.commit()
        return member
    except (WorkspaceNotFoundError, NotFoundError) as e:
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{id}/members", response_model=List[WorkspaceMemberResponseDto])
async def list_members(
    id: UUID,
    current_user: User = Depends(get_current_user),
    repo: SQLWorkspaceRepository = Depends(get_workspace_repository),
):
    use_case = ListMembers(repo)
    try:
        return await use_case.execute(id, current_user)
    except WorkspaceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UnauthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/{id}/members/{user_id}", response_model=WorkspaceMemberResponseDto)
async def update_member_role(
    id: UUID,
    user_id: UUID,
    data: UpdateMemberRoleRequestDto,
    current_user: User = Depends(get_current_user),
    repo: SQLWorkspaceRepository = Depends(get_workspace_repository),
    session: AsyncSession = Depends(get_db),
):
    use_case = UpdateMemberRole(repo)
    try:
        member = await use_case.execute(id, user_id, current_user, data)
        await session.commit()
        return member
    except (WorkspaceNotFoundError, MemberNotFoundError) as e:
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/{id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    repo: SQLWorkspaceRepository = Depends(get_workspace_repository),
    session: AsyncSession = Depends(get_db),
):
    use_case = RemoveMember(repo)
    try:
        await use_case.execute(id, user_id, current_user)
        await session.commit()
    except (WorkspaceNotFoundError, MemberNotFoundError) as e:
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
