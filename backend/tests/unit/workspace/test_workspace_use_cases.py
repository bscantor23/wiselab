import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from src.application.use_cases.workspace.create.index import CreateWorkspace
from src.application.use_cases.workspace.list.index import ListWorkspaces
from src.application.use_cases.workspace.get.index import GetWorkspace
from src.application.use_cases.workspace.update.index import UpdateWorkspace
from src.application.use_cases.workspace.delete.index import DeleteWorkspace
from src.application.use_cases.workspace.members.invite.index import InviteMember
from src.application.use_cases.workspace.members.list.index import ListMembers
from src.application.use_cases.workspace.members.update.index import UpdateMemberRole
from src.application.use_cases.workspace.members.remove.index import RemoveMember
from src.application.use_cases.workspace.create.dtos import CreateWorkspaceRequestDto
from src.application.use_cases.workspace.update.dtos import UpdateWorkspaceRequestDto
from src.application.use_cases.workspace.members.invite.dtos import InviteMemberRequestDto
from src.application.use_cases.workspace.members.update.dtos import UpdateMemberRoleRequestDto
from src.domain.workspace.models import Workspace, WorkspaceMember
from src.domain.workspace.value_objects import WorkspaceRole
from src.domain.auth.models import User
from src.domain.auth.value_objects import Email
from src.domain.errors import (
    WorkspaceNotFoundError, UnauthorizedError, ValidationError, NotFoundError, MemberNotFoundError, ConflictError
)

@pytest.mark.asyncio
async def test_create_workspace(mock_workspace_repo, mock_user_entity):
    use_case = CreateWorkspace(mock_workspace_repo)
    data = CreateWorkspaceRequestDto(name="New Workspace", description="Desc")

    result = await use_case.execute(mock_user_entity, data)

    assert result.name == "New Workspace"
    assert result.owner_id == mock_user_entity.id
    assert mock_workspace_repo.add.called
    assert mock_workspace_repo.add_member.called

@pytest.mark.asyncio
async def test_create_workspace_duplicate_name(mock_workspace_repo, mock_user_entity, mock_workspace_entity):
    mock_workspace_repo.get_by_name_and_owner = AsyncMock(return_value=mock_workspace_entity)
    use_case = CreateWorkspace(mock_workspace_repo)
    data = CreateWorkspaceRequestDto(name=mock_workspace_entity.name)

    with pytest.raises(ConflictError):
        await use_case.execute(mock_user_entity, data)

@pytest.mark.asyncio
async def test_list_workspaces(mock_workspace_repo, mock_user_entity, mock_workspace_entity):
    mock_workspace_repo.list_by_user = AsyncMock(return_value=[mock_workspace_entity])
    use_case = ListWorkspaces(mock_workspace_repo)
    
    result = await use_case.execute(mock_user_entity)
    assert len(result) == 1
    assert result[0].id == mock_workspace_entity.id

@pytest.mark.asyncio
async def test_get_workspace_success_owner(mock_workspace_repo, mock_user_entity, mock_workspace_entity):
    mock_workspace_repo.get_by_id = AsyncMock(return_value=mock_workspace_entity)
    use_case = GetWorkspace(mock_workspace_repo)
    
    result = await use_case.execute(mock_workspace_entity.id, mock_user_entity)
    assert result == mock_workspace_entity

@pytest.mark.asyncio
async def test_get_workspace_success_member(mock_workspace_repo, mock_user_entity):
    # Owner different, user is member
    ws = Workspace(name="Test", owner_id=uuid4(), id=uuid4())
    mock_workspace_repo.get_by_id = AsyncMock(return_value=ws)
    
    member = MagicMock(spec=WorkspaceMember)
    mock_workspace_repo.get_member.return_value = member
    
    use_case = GetWorkspace(mock_workspace_repo)
    result = await use_case.execute(ws.id, mock_user_entity)
    assert result == ws

@pytest.mark.asyncio
async def test_invite_member_success_admin(mock_workspace_repo, mock_user_repo, mock_user_entity):
    # Workspace where user is NOT owner
    ws = Workspace(name="Test", owner_id=uuid4(), id=uuid4())
    mock_workspace_repo.get_by_id = AsyncMock(return_value=ws)
    
    # User is ADMIN
    admin_member = MagicMock(spec=WorkspaceMember)
    admin_member.role = WorkspaceRole.ADMIN
    
    # First call: get_member(inviter) -> admin_member
    # Second call: get_member(invitee) -> None
    mock_workspace_repo.get_member.side_effect = [admin_member, None]
    
    # Invitee setup
    invitee = MagicMock(spec=User)
    invitee.id = uuid4()
    mock_user_repo.get_by_email.return_value = invitee
    
    use_case = InviteMember(mock_workspace_repo, mock_user_repo)
    data = InviteMemberRequestDto(email="new@example.com")
    
    result = await use_case.execute(ws.id, mock_user_entity, data)
    assert result.user_id == invitee.id
    assert mock_workspace_repo.add_member.called

@pytest.mark.asyncio
async def test_get_workspace_not_found(mock_workspace_repo, mock_user_entity):
    mock_workspace_repo.get_by_id = AsyncMock(return_value=None)
    use_case = GetWorkspace(mock_workspace_repo)
    
    with pytest.raises(WorkspaceNotFoundError):
        await use_case.execute(uuid4(), mock_user_entity)

@pytest.mark.asyncio
async def test_get_workspace_unauthorized_not_member(mock_workspace_repo, mock_user_entity):
    # Setup non-owner user
    ws = Workspace(name="Test", owner_id=uuid4(), id=uuid4())
    mock_workspace_repo.get_by_id = AsyncMock(return_value=ws)
    mock_workspace_repo.get_member = AsyncMock(return_value=None)
    
    use_case = GetWorkspace(mock_workspace_repo)
    with pytest.raises(UnauthorizedError):
        await use_case.execute(ws.id, mock_user_entity)

@pytest.mark.asyncio
async def test_update_workspace_success_owner(mock_workspace_repo, mock_user_entity, mock_workspace_entity):
    mock_workspace_repo.get_by_id = AsyncMock(return_value=mock_workspace_entity)
    use_case = UpdateWorkspace(mock_workspace_repo)
    data = UpdateWorkspaceRequestDto(name="Updated Name")
    
    result = await use_case.execute(mock_workspace_entity.id, mock_user_entity, data)
    assert result.name == "Updated Name"
    assert mock_workspace_repo.update.called

@pytest.mark.asyncio
async def test_update_workspace_description_only(mock_workspace_repo, mock_user_entity, mock_workspace_entity):
    mock_workspace_repo.get_by_id = AsyncMock(return_value=mock_workspace_entity)
    use_case = UpdateWorkspace(mock_workspace_repo)
    # Name is None, description provided
    data = UpdateWorkspaceRequestDto(name=None, description="New Desc")
    
    result = await use_case.execute(mock_workspace_entity.id, mock_user_entity, data)
    assert result.description == "New Desc"
    assert mock_workspace_repo.update.called

@pytest.mark.asyncio
async def test_update_workspace_duplicate_name(mock_workspace_repo, mock_user_entity, mock_workspace_entity):
    # Current workspace
    mock_workspace_repo.get_by_id = AsyncMock(return_value=mock_workspace_entity)
    
    # Another workspace with the same desired name
    another_ws = Workspace(name="Existing Name", owner_id=mock_user_entity.id, id=uuid4())
    mock_workspace_repo.get_by_name_and_owner = AsyncMock(return_value=another_ws)
    
    use_case = UpdateWorkspace(mock_workspace_repo)
    data = UpdateWorkspaceRequestDto(name="Existing Name")
    
    with pytest.raises(ConflictError):
        await use_case.execute(mock_workspace_entity.id, mock_user_entity, data)

@pytest.mark.asyncio
async def test_update_workspace_success_admin(mock_workspace_repo, mock_user_entity):
    # Owner different, user is admin
    ws = Workspace(name="Test", owner_id=uuid4(), id=uuid4())
    mock_workspace_repo.get_by_id = AsyncMock(return_value=ws)
    
    admin_member = MagicMock(spec=WorkspaceMember)
    admin_member.role = WorkspaceRole.ADMIN
    mock_workspace_repo.get_member.return_value = admin_member
    
    use_case = UpdateWorkspace(mock_workspace_repo)
    data = UpdateWorkspaceRequestDto(name="Updated Name")
    
    result = await use_case.execute(ws.id, mock_user_entity, data)
    assert result.name == "Updated Name"

@pytest.mark.asyncio
async def test_update_workspace_unauthorized(mock_workspace_repo, mock_user_entity):
    ws = Workspace(name="Test", owner_id=uuid4(), id=uuid4())
    mock_workspace_repo.get_by_id = AsyncMock(return_value=ws)
    
    viewer_member = MagicMock(spec=WorkspaceMember)
    viewer_member.role = WorkspaceRole.VIEWER
    mock_workspace_repo.get_member.return_value = viewer_member
    
    use_case = UpdateWorkspace(mock_workspace_repo)
    data = UpdateWorkspaceRequestDto(name="Updated Name")
    
    with pytest.raises(UnauthorizedError):
        await use_case.execute(ws.id, mock_user_entity, data)

@pytest.mark.asyncio
async def test_update_workspace_not_found(mock_workspace_repo, mock_user_entity):
    mock_workspace_repo.get_by_id.return_value = None
    use_case = UpdateWorkspace(mock_workspace_repo)
    with pytest.raises(WorkspaceNotFoundError):
        await use_case.execute(uuid4(), mock_user_entity, UpdateWorkspaceRequestDto(name="ValidName"))

@pytest.mark.asyncio
async def test_delete_workspace_success(mock_workspace_repo, mock_user_entity, mock_workspace_entity):
    mock_workspace_repo.get_by_id = AsyncMock(return_value=mock_workspace_entity)
    use_case = DeleteWorkspace(mock_workspace_repo)
    await use_case.execute(mock_workspace_entity.id, mock_user_entity)
    assert mock_workspace_repo.remove.called

@pytest.mark.asyncio
async def test_delete_workspace_unauthorized(mock_workspace_repo, mock_user_entity):
    ws = Workspace(name="Test", owner_id=uuid4(), id=uuid4())
    mock_workspace_repo.get_by_id = AsyncMock(return_value=ws)
    use_case = DeleteWorkspace(mock_workspace_repo)
    with pytest.raises(UnauthorizedError):
        await use_case.execute(ws.id, mock_user_entity)

@pytest.mark.asyncio
async def test_delete_workspace_not_found(mock_workspace_repo, mock_user_entity):
    mock_workspace_repo.get_by_id.return_value = None
    use_case = DeleteWorkspace(mock_workspace_repo)
    with pytest.raises(WorkspaceNotFoundError):
        await use_case.execute(uuid4(), mock_user_entity)

@pytest.mark.asyncio
async def test_invite_member_full_logic(mock_workspace_repo, mock_user_repo, mock_user_entity, mock_workspace_entity):
    # Success Case
    mock_workspace_repo.get_by_id.return_value = mock_workspace_entity
    invitee = MagicMock(spec=User)
    invitee.id = uuid4()
    mock_user_repo.get_by_email.return_value = invitee
    mock_workspace_repo.get_member.return_value = None
    
    use_case = InviteMember(mock_workspace_repo, mock_user_repo)
    data = InviteMemberRequestDto(email="new@example.com")
    result = await use_case.execute(mock_workspace_entity.id, mock_user_entity, data)
    assert result.user_id == invitee.id

    # Not found workspace
    mock_workspace_repo.get_by_id.return_value = None
    with pytest.raises(WorkspaceNotFoundError):
        await use_case.execute(uuid4(), mock_user_entity, data)
    mock_workspace_repo.get_by_id.return_value = mock_workspace_entity

    # Unauthorized (viewer inviting) - inviter exists but role is VIEWER
    ws_other = Workspace(name="Other", owner_id=uuid4(), id=uuid4())
    mock_workspace_repo.get_by_id.return_value = ws_other
    viewer = MagicMock(spec=WorkspaceMember)
    viewer.role = WorkspaceRole.VIEWER
    mock_workspace_repo.get_member.return_value = viewer
    with pytest.raises(UnauthorizedError):
        await use_case.execute(ws_other.id, mock_user_entity, data)
    
    # Unauthorized (inviter is None/Not found in WS)
    mock_workspace_repo.get_member.return_value = None
    with pytest.raises(UnauthorizedError):
        await use_case.execute(ws_other.id, mock_user_entity, data)

    mock_workspace_repo.get_by_id.return_value = mock_workspace_entity

    # Invalid Email format (mocked at usage source technically, but DTO validates)
    # Testing Validation Error re-raise
    with pytest.raises(ValidationError):
        await use_case.execute(mock_workspace_entity.id, mock_user_entity, InviteMemberRequestDto(email="invalid-email"))

    # User not found
    mock_user_repo.get_by_email.return_value = None
    with pytest.raises(NotFoundError):
        await use_case.execute(mock_workspace_entity.id, mock_user_entity, data)
    mock_user_repo.get_by_email.return_value = invitee

    # Already owner
    invitee.id = mock_workspace_entity.owner_id
    with pytest.raises(ValidationError):
        await use_case.execute(mock_workspace_entity.id, mock_user_entity, data)
    invitee.id = uuid4() 

    # Already member
    mock_workspace_repo.get_member.return_value = MagicMock()
    with pytest.raises(ValidationError):
        await use_case.execute(mock_workspace_entity.id, mock_user_entity, data)
    mock_workspace_repo.get_member.return_value = None

    # Cannot invite as OWNER
    data_owner = InviteMemberRequestDto(email="a@a.com", role=WorkspaceRole.OWNER)
    with pytest.raises(ValidationError):
        await use_case.execute(mock_workspace_entity.id, mock_user_entity, data_owner)

@pytest.mark.asyncio
async def test_list_members_logic(mock_workspace_repo, mock_user_entity, mock_workspace_entity):
    mock_workspace_repo.get_by_id.return_value = mock_workspace_entity
    mock_workspace_repo.list_members.return_value = []
    
    use_case = ListMembers(mock_workspace_repo)
    await use_case.execute(mock_workspace_entity.id, mock_user_entity)
    
    # Not found
    mock_workspace_repo.get_by_id.return_value = None
    with pytest.raises(WorkspaceNotFoundError):
        await use_case.execute(uuid4(), mock_user_entity)
    mock_workspace_repo.get_by_id.return_value = mock_workspace_entity
    
@pytest.mark.asyncio
async def test_list_members_success_member(mock_workspace_repo, mock_user_entity):
    # Workspace not owned by user
    ws = Workspace(name="Test", owner_id=uuid4(), id=uuid4())
    mock_workspace_repo.get_by_id.return_value = ws
    
    # User is a member
    member = MagicMock(spec=WorkspaceMember)
    mock_workspace_repo.get_member.return_value = member
    mock_workspace_repo.list_members.return_value = []
    
    use_case = ListMembers(mock_workspace_repo)
    result = await use_case.execute(ws.id, mock_user_entity)
    assert result == []

@pytest.mark.asyncio
async def test_list_members_unauthorized(mock_workspace_repo, mock_user_entity):
    # Unauthorized (non-member accessing)
    ws_other = Workspace(name="Other", owner_id=uuid4(), id=uuid4())
    mock_workspace_repo.get_by_id.return_value = ws_other
    mock_workspace_repo.get_member.return_value = None
    
    use_case = ListMembers(mock_workspace_repo)
    with pytest.raises(UnauthorizedError):
        await use_case.execute(ws_other.id, mock_user_entity)

@pytest.mark.asyncio
async def test_update_member_role_logic(mock_workspace_repo, mock_user_entity, mock_workspace_entity):
    mock_workspace_repo.get_by_id.return_value = mock_workspace_entity
    member_id = uuid4()
    real_member = WorkspaceMember(workspace_id=mock_workspace_entity.id, user_id=member_id, role=WorkspaceRole.VIEWER, id=member_id)
    mock_workspace_repo.get_member.return_value = real_member
    
    use_case = UpdateMemberRole(mock_workspace_repo)
    data = UpdateMemberRoleRequestDto(role=WorkspaceRole.EDITOR)
    
    # Success
    res = await use_case.execute(mock_workspace_entity.id, member_id, mock_user_entity, data)
    assert res.role == WorkspaceRole.EDITOR

    # Not Found WS
    mock_workspace_repo.get_by_id.return_value = None
    with pytest.raises(WorkspaceNotFoundError):
        await use_case.execute(uuid4(), member_id, mock_user_entity, data)
    mock_workspace_repo.get_by_id.return_value = mock_workspace_entity

    # Unauthorized
    ws_other = Workspace(name="Other", owner_id=uuid4(), id=uuid4())
    mock_workspace_repo.get_by_id.return_value = ws_other
    mock_workspace_repo.get_member.side_effect = [
        MagicMock(role=WorkspaceRole.VIEWER), # Current user (not admin)
        real_member
    ]
    with pytest.raises(UnauthorizedError):
        await use_case.execute(ws_other.id, member_id, mock_user_entity, data)
    
    mock_workspace_repo.get_member.side_effect = None
    mock_workspace_repo.get_member.return_value = real_member

    # Cannot update owner
    # ws owner id same as member_id
    ws_owner_member = Workspace(name="Own", owner_id=member_id, id=uuid4())
    mock_workspace_repo.get_by_id.return_value = ws_owner_member
    # Permission ok (user is owner/admin?) No, user is calling.
    # We need to pass permission check first. 
    # Current user is mock_user_entity. ws owner is member_id.
    # Just need to pass auth check. Let's make current user admin.
    admin_caller = MagicMock(role=WorkspaceRole.ADMIN)
    mock_workspace_repo.get_member.side_effect = None
    mock_workspace_repo.get_member.return_value = admin_caller # Logic uses get_member(user_id) first if not owner
    
    # Wait, logic is:
    # 1. Check workspace existence
    # 2. Check permission (owner or admin)
    # 3. Check target is not owner
    # 4. Check target exists
    # 5. Check role change valid (not to owner)
    
    # So to fail step 3, we need to pass step 2.
    ws_owner_is_target = Workspace(name="O", owner_id=member_id, id=uuid4())
    # Current user needs to be admin (since they are not owner)
    mock_workspace_repo.get_by_id.return_value = ws_owner_is_target
    mock_workspace_repo.get_member.side_effect = None
    mock_workspace_repo.get_member.return_value = MagicMock(role=WorkspaceRole.ADMIN) 
    
    with pytest.raises(ValidationError):
        await use_case.execute(ws_owner_is_target.id, member_id, mock_user_entity, data)

    # Member not found
    mock_workspace_repo.get_by_id.return_value = mock_workspace_entity
    mock_workspace_repo.get_member.return_value = None
    with pytest.raises(MemberNotFoundError):
        await use_case.execute(mock_workspace_entity.id, member_id, mock_user_entity, data)
    mock_workspace_repo.get_member.return_value = real_member

    # Cannot set to OWNER
    data_owner = UpdateMemberRoleRequestDto(role=WorkspaceRole.OWNER)
    with pytest.raises(ValidationError):
        await use_case.execute(mock_workspace_entity.id, member_id, mock_user_entity, data_owner)

@pytest.mark.asyncio
async def test_remove_member_logic(mock_workspace_repo, mock_user_entity, mock_workspace_entity):
    mock_workspace_repo.get_by_id.return_value = mock_workspace_entity
    member_id = uuid4()
    mock_member = MagicMock(spec=WorkspaceMember)
    mock_member.user_id = member_id
    mock_workspace_repo.get_member.return_value = mock_member
    
    use_case = RemoveMember(mock_workspace_repo)
    
    # Success
    await use_case.execute(mock_workspace_entity.id, member_id, mock_user_entity)
    
    # Not found WS
    mock_workspace_repo.get_by_id.return_value = None
    with pytest.raises(WorkspaceNotFoundError):
        await use_case.execute(uuid4(), member_id, mock_user_entity)
    mock_workspace_repo.get_by_id.return_value = mock_workspace_entity
    
    # Unauthorized
    ws_other = Workspace(name="Other", owner_id=uuid4(), id=uuid4())
    mock_workspace_repo.get_by_id.return_value = ws_other
    mock_workspace_repo.get_member.side_effect = [
        MagicMock(role=WorkspaceRole.VIEWER), # Current user
        mock_member
    ]
    with pytest.raises(UnauthorizedError):
        await use_case.execute(ws_other.id, member_id, mock_user_entity)
    
    mock_workspace_repo.get_member.side_effect = None
    mock_workspace_repo.get_member.return_value = mock_member

    # Cannot remove owner
    ws_tgt_owner = Workspace(name="Tgt", owner_id=member_id, id=uuid4())
    mock_workspace_repo.get_by_id.return_value = ws_tgt_owner
    # Caller needs permission
    mock_workspace_repo.get_member.return_value = MagicMock(role=WorkspaceRole.ADMIN)
    
    with pytest.raises(ValidationError):
        await use_case.execute(ws_tgt_owner.id, member_id, mock_user_entity)
    
    # Member not found
    mock_workspace_repo.get_by_id.return_value = mock_workspace_entity
    mock_workspace_repo.get_member.return_value = None
    with pytest.raises(MemberNotFoundError):
        await use_case.execute(mock_workspace_entity.id, member_id, mock_user_entity)
