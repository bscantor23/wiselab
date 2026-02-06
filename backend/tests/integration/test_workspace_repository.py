import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.workspace.repositories import SQLWorkspaceRepository
from src.infrastructure.auth.repositories import SQLUserRepository
from src.domain.workspace.models import Workspace, WorkspaceMember
from src.domain.workspace.value_objects import WorkspaceRole
from src.domain.auth.models import User
from src.domain.auth.value_objects import Email

@pytest.mark.asyncio
async def test_workspace_repository_flow(db_session: AsyncSession):
    workspace_repo = SQLWorkspaceRepository(db_session)
    user_repo = SQLUserRepository(db_session)
    
    # 1. Create owner
    owner_email = Email("owner@example.com")
    owner = User(email=owner_email, password_hash="hash", full_name="Owner User")
    await user_repo.add(owner)
    await db_session.commit()
    
    # 2. Create workspace
    workspace = Workspace(
        name="Test Workspace",
        description="A test workspace",
        owner_id=owner.id
    )
    await workspace_repo.add(workspace)
    await db_session.commit()
    
    # 3. Get workspace by ID
    found = await workspace_repo.get_by_id(workspace.id)
    assert found is not None
    assert found.name == "Test Workspace"
    assert found.owner_id == owner.id
    
    # 4. List by user (owner)
    workspaces = await workspace_repo.list_by_user(owner.id)
    assert len(workspaces) == 1
    assert workspaces[0].id == workspace.id
    
    # 5. Add member
    member_user = User(email=Email("member@example.com"), password_hash="hash", full_name="Member User")
    await user_repo.add(member_user)
    await db_session.commit()
    
    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=member_user.id,
        role=WorkspaceRole.VIEWER
    )
    await workspace_repo.add_member(member)
    await db_session.commit()
    
    # 6. List by user (member)
    member_workspaces = await workspace_repo.list_by_user(member_user.id)
    assert len(member_workspaces) == 1
    assert member_workspaces[0].id == workspace.id
    
    # 7. Get member
    found_member = await workspace_repo.get_member(workspace.id, member_user.id)
    assert found_member is not None
    assert found_member.role == WorkspaceRole.VIEWER
    
    # 8. Get synthetic member (owner)
    found_owner = await workspace_repo.get_member(workspace.id, owner.id)
    assert found_owner is not None
    assert found_owner.role == WorkspaceRole.OWNER
    
    # 9. List members
    members = await workspace_repo.list_members(workspace.id)
    assert len(members) == 2
    assert any(m.role == WorkspaceRole.OWNER for m in members)
    assert any(m.role == WorkspaceRole.VIEWER for m in members)
    
    # 10. Update member role
    found_member.change_role(WorkspaceRole.ADMIN)
    await workspace_repo.update_member(found_member)
    await db_session.commit()
    
    updated_member = await workspace_repo.get_member(workspace.id, member_user.id)
    assert updated_member.role == WorkspaceRole.ADMIN
    
    # 11. Update workspace
    workspace.update_details(name="Updated Workspace")
    await workspace_repo.update(workspace)
    await db_session.commit()
    
    found_updated = await workspace_repo.get_by_id(workspace.id)
    assert found_updated.name == "Updated Workspace"
    
    # 12. List all (admin view)
    all_workspaces = await workspace_repo.list()
    assert len(all_workspaces) >= 1
    
    # 13. Remove member
    await workspace_repo.remove_member(workspace.id, member_user.id)
    await db_session.commit()
    assert await workspace_repo.get_member(workspace.id, member_user.id) is None
    
    # 14. Remove workspace
    await workspace_repo.remove(workspace)
    await db_session.commit()
    assert await workspace_repo.get_by_id(workspace.id) is None
