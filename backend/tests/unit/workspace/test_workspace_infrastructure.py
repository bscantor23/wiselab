import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from src.infrastructure.workspace.repositories import SQLWorkspaceRepository
from src.domain.workspace.models import Workspace, WorkspaceMember
from src.domain.workspace.value_objects import WorkspaceRole
from src.infrastructure.workspace.models import WorkspaceORM, WorkspaceMemberORM

@pytest.mark.asyncio
async def test_repo_add_and_get():
    session = AsyncMock()
    session.add = MagicMock()
    repo = SQLWorkspaceRepository(session)
    
    ws = Workspace(name="Repo Test", owner_id=uuid4())
    await repo.add(ws)
    session.add.assert_called()
    
    # Test get_by_id success
    session.execute = AsyncMock()
    result = MagicMock()
    orm_ws = WorkspaceORM(
        id=ws.id, name=ws.name, description=ws.description, 
        owner_id=ws.owner_id, is_active=True, created_at=ws.created_at, updated_at=ws.updated_at
    )
    result.scalar_one_or_none.return_value = orm_ws
    session.execute.return_value = result
    
    fetched = await repo.get_by_id(ws.id)
    assert fetched.id == ws.id
    
    # Test get_by_id None
    result.scalar_one_or_none.return_value = None
    fetched_none = await repo.get_by_id(ws.id)
    assert fetched_none is None

@pytest.mark.asyncio
async def test_repo_list_by_user():
    session = AsyncMock()
    repo = SQLWorkspaceRepository(session)
    user_id = uuid4()
    
    session.execute = AsyncMock()
    result = MagicMock()
    orm_ws = WorkspaceORM(id=uuid4(), name="List", owner_id=user_id)
    result.scalars.return_value = [orm_ws]
    session.execute.return_value = result
    
    items = await repo.list_by_user(user_id)
    assert len(items) == 1
    assert items[0].owner_id == user_id

@pytest.mark.asyncio
async def test_repo_member_operations():
    session = AsyncMock()
    session.add = MagicMock()
    repo = SQLWorkspaceRepository(session)
    
    member = WorkspaceMember(workspace_id=uuid4(), user_id=uuid4(), role=WorkspaceRole.VIEWER)
    
    # Add
    await repo.add_member(member)
    session.add.assert_called()
    
    # Update
    await repo.update_member(member)
    session.execute.assert_called()
    
    # Remove
    await repo.remove_member(member.workspace_id, member.user_id)
    session.execute.assert_called()
    
    # Get Member Success (mock both workspace and member queries)
    session.execute = AsyncMock()
    
    # First call returns None for workspace (not owner check)
    workspace_res = MagicMock()
    workspace_res.scalar_one_or_none.return_value = None
    
    # Second call returns member
    member_res = MagicMock()
    orm_mem = WorkspaceMemberORM(
        id=member.id, workspace_id=member.workspace_id, user_id=member.user_id, role="viewer"
    )
    member_res.scalar_one_or_none.return_value = orm_mem
    
    session.execute.side_effect = [workspace_res, member_res]
    
    fetched = await repo.get_member(member.workspace_id, member.user_id)
    assert fetched.user_id == member.user_id
    
    # Get Member None (both queries return None)
    workspace_res_none = MagicMock()
    workspace_res_none.scalar_one_or_none.return_value = None
    member_res_none = MagicMock()
    member_res_none.scalar_one_or_none.return_value = None
    session.execute.side_effect = [workspace_res_none, member_res_none]
    
    fetched_none = await repo.get_member(member.workspace_id, member.user_id)
    assert fetched_none is None

@pytest.mark.asyncio
async def test_repo_list_members():
    session = AsyncMock()
    repo = SQLWorkspaceRepository(session)
    
    workspace_id = uuid4()
    owner_id = uuid4()
    
    # First call gets workspace (to add owner)
    workspace_res = MagicMock()
    orm_workspace = WorkspaceORM(id=workspace_id, owner_id=owner_id)
    workspace_res.scalar_one_or_none.return_value = orm_workspace
    
    # Second call gets members list
    members_res = MagicMock()
    orm_mem = WorkspaceMemberORM(id=uuid4(), role="editor")
    members_res.scalars.return_value = [orm_mem]
    
    session.execute.side_effect = [workspace_res, members_res]
    
    items = await repo.list_members(workspace_id)
    # Should have owner + 1 regular member = 2 total
    assert len(items) == 2
    # First member should be owner
    assert items[0].role == WorkspaceRole.OWNER
    assert items[0].user_id == owner_id

@pytest.mark.asyncio
async def test_repo_update_remove_workspace():
    session = AsyncMock()
    repo = SQLWorkspaceRepository(session)
    ws = Workspace(name="Up", owner_id=uuid4())
    
    await repo.update(ws)
    session.execute.assert_called()
    
    await repo.remove(ws)
    session.execute.assert_called()

@pytest.mark.asyncio
async def test_repo_list_all():
    session = AsyncMock()
    repo = SQLWorkspaceRepository(session)
    
    res = MagicMock()
    orm_ws = WorkspaceORM(id=uuid4(), name="All")
    res.scalars.return_value = [orm_ws]
    session.execute.return_value = res
    
    items = await repo.list()
    assert len(items) == 1
