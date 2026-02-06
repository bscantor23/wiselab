import pytest
from datetime import datetime
from uuid import uuid4
from src.domain.workspace.models import Workspace, WorkspaceMember
from src.domain.workspace.value_objects import WorkspaceRole

def test_workspace_creation():
    owner_id = uuid4()
    ws = Workspace(name="Test", owner_id=owner_id, description="Desc")
    assert ws.name == "Test"
    assert ws.owner_id == owner_id
    assert ws.is_active is True
    assert isinstance(ws.created_at, datetime)

def test_workspace_update_details():
    owner_id = uuid4()
    ws = Workspace(name="Old", owner_id=owner_id)
    old_updated = ws.updated_at
    
    import time
    time.sleep(0.001)
    
    ws.update_details(name="New", description="New Desc")
    assert ws.name == "New"
    assert ws.description == "New Desc"
    assert ws.updated_at > old_updated

def test_workspace_member_creation():
    uid = uuid4()
    wid = uuid4()
    member = WorkspaceMember(workspace_id=wid, user_id=uid, role=WorkspaceRole.VIEWER)
    assert member.user_id == uid
    assert member.role == WorkspaceRole.VIEWER

def test_member_change_role():
    uid = uuid4()
    wid = uuid4()
    member = WorkspaceMember(workspace_id=wid, user_id=uid, role=WorkspaceRole.VIEWER)
    member.change_role(WorkspaceRole.ADMIN)
    assert member.role == WorkspaceRole.ADMIN

def test_role_enum_values():
    assert WorkspaceRole.OWNER == "owner"
    assert WorkspaceRole.ADMIN == "admin"
    assert WorkspaceRole.EDITOR == "editor"
    assert WorkspaceRole.VIEWER == "viewer"
