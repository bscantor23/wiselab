import pytest
import uuid
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch
from src.domain.errors import (
    WorkspaceNotFoundError, UnauthorizedError, ValidationError, NotFoundError, MemberNotFoundError
)
from src.domain.workspace.models import Workspace, WorkspaceMember
from src.domain.workspace.value_objects import WorkspaceRole
from datetime import datetime
from src.api.dependencies.auth import get_current_user, get_user_repository
from src.api.dependencies.workspace import get_workspace_repository
from src.infrastructure.database import get_db

@pytest.fixture
def mock_user_obj():
    mock = MagicMock()
    mock.id = uuid.uuid4()
    mock.email = "test@example.com"
    mock.is_active = True
    return mock

@pytest.mark.asyncio
async def test_create_workspace_route(mock_user_obj):
    from src.api.main import app
    
    mock_repo = AsyncMock()
    mock_repo.add = AsyncMock()
    mock_repo.add_member = AsyncMock()

    app.dependency_overrides[get_current_user] = lambda: mock_user_obj
    app.dependency_overrides[get_workspace_repository] = lambda: mock_repo
    app.dependency_overrides[get_db] = lambda: AsyncMock()

    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {"name": "New", "description": "Desc"}
        resp = await client.post("/workspaces", json=payload)
        assert resp.status_code == 201
        assert resp.json()["name"] == "New"
        
    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_list_workspaces_route(mock_user_obj):
    from src.api.main import app
    mock_repo = AsyncMock()
    mock_repo.list_by_user = AsyncMock(return_value=[])

    app.dependency_overrides[get_current_user] = lambda: mock_user_obj
    app.dependency_overrides[get_workspace_repository] = lambda: mock_repo

    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.get("/workspaces")
        assert resp.status_code == 200
        assert resp.json() == []

    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_get_workspace_route(mock_user_obj):
    from src.api.main import app
    wid = uuid.uuid4()
    mock_repo = AsyncMock()
    
    # Success
    ws_real = Workspace(name="Test", description="Desc", owner_id=mock_user_obj.id, id=wid)
    mock_repo.get_by_id.return_value = ws_real

    app.dependency_overrides[get_current_user] = lambda: mock_user_obj
    app.dependency_overrides[get_workspace_repository] = lambda: mock_repo
    app.dependency_overrides[get_db] = lambda: AsyncMock()

    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.get(f"/workspaces/{wid}")
        assert resp.status_code == 200
        assert resp.json()["id"] == str(wid)
        
    # Not Found
    mock_repo.get_by_id.return_value = None
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.get(f"/workspaces/{wid}")
        assert resp.status_code == 404

    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_update_workspace_route(mock_user_obj):
    from src.api.main import app
    wid = uuid.uuid4()
    mock_repo = AsyncMock()
    # Success owner
    ws_real = Workspace(name="Old", description="Desc", owner_id=mock_user_obj.id, id=wid)
    mock_repo.get_by_id.return_value = ws_real
    mock_repo.update = AsyncMock()

    app.dependency_overrides[get_current_user] = lambda: mock_user_obj
    app.dependency_overrides[get_workspace_repository] = lambda: mock_repo
    app.dependency_overrides[get_db] = lambda: AsyncMock()

    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.put(f"/workspaces/{wid}", json={"name": "New Name"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "New Name"
        
    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_delete_workspace_route(mock_user_obj):
    from src.api.main import app
    wid = uuid.uuid4()
    mock_repo = AsyncMock()
    # Success owner
    ws_real = Workspace(name="Del", owner_id=mock_user_obj.id, id=wid)
    mock_repo.get_by_id.return_value = ws_real
    mock_repo.remove = AsyncMock()

    app.dependency_overrides[get_current_user] = lambda: mock_user_obj
    app.dependency_overrides[get_workspace_repository] = lambda: mock_repo
    app.dependency_overrides[get_db] = lambda: AsyncMock()

    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.delete(f"/workspaces/{wid}")
        assert resp.status_code == 204

    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_member_routes(mock_user_obj):
    from src.api.main import app
    wid = uuid.uuid4()
    uid = uuid.uuid4()
    
    mock_ws_repo = AsyncMock()
    mock_user_repo = AsyncMock()
    
    # Success owner logic setup for workspace retrieval
    ws_real = Workspace(name="Mem", owner_id=mock_user_obj.id, id=wid)
    mock_ws_repo.get_by_id.return_value = ws_real
    
    # User to invite
    invitee = MagicMock()
    invitee.id = uid
    invitee.email = "new@test.com"
    mock_user_repo.get_by_email.return_value = invitee
    
    mock_ws_repo.get_member.return_value = None # Not member yet
    mock_ws_repo.add_member = AsyncMock()

    app.dependency_overrides[get_current_user] = lambda: mock_user_obj
    app.dependency_overrides[get_workspace_repository] = lambda: mock_ws_repo
    app.dependency_overrides[get_user_repository] = lambda: mock_user_repo
    app.dependency_overrides[get_db] = lambda: AsyncMock()

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Invite
        resp = await client.post(f"/workspaces/{wid}/members", json={"email": "new@test.com", "role": "viewer"})
        assert resp.status_code == 201
        
        # List
        mock_ws_repo.list_members.return_value = []
        resp = await client.get(f"/workspaces/{wid}/members")
        assert resp.status_code == 200

        # Update Role (need member to exist)
        member_real = WorkspaceMember(workspace_id=wid, user_id=uid, role=WorkspaceRole.VIEWER, id=uuid.uuid4())
        # Mock get_member to return member now
        mock_ws_repo.get_member.return_value = member_real
        mock_ws_repo.update_member = AsyncMock()
        
        resp = await client.put(f"/workspaces/{wid}/members/{uid}", json={"role": "editor"})
        assert resp.status_code == 200
        assert resp.json()["role"] == "editor"
        
        # Remove
        mock_ws_repo.remove_member = AsyncMock()
        resp = await client.delete(f"/workspaces/{wid}/members/{uid}")
        assert resp.status_code == 204

    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_api_exception_handling(mock_user_obj):
    """Test all exception branches in API routes by mocking Use Case execution"""
    from src.api.main import app
    
    # We mock the repository to just pass dependency injection
    mock_repo = AsyncMock() 
    app.dependency_overrides[get_current_user] = lambda: mock_user_obj
    app.dependency_overrides[get_workspace_repository] = lambda: mock_repo
    app.dependency_overrides[get_user_repository] = lambda: AsyncMock()
    app.dependency_overrides[get_db] = lambda: AsyncMock()

    async with AsyncClient(app=app, base_url="http://test") as client:
        wid = str(uuid.uuid4())
        uid = str(uuid.uuid4())

        # 1. Create Workspace Exceptions
        with patch("src.application.use_cases.workspace.create.index.CreateWorkspace.execute", side_effect=ValidationError("Invalid")):
            resp = await client.post("/workspaces", json={"name": "Bad"})
            assert resp.status_code == 400
        with patch("src.application.use_cases.workspace.create.index.CreateWorkspace.execute", side_effect=Exception("Sever Error")):
            resp = await client.post("/workspaces", json={"name": "Crash"})
            assert resp.status_code == 500

        # 2. Get Workspace Exceptions
        with patch("src.application.use_cases.workspace.get.index.GetWorkspace.execute", side_effect=WorkspaceNotFoundError("Gone")):
            resp = await client.get(f"/workspaces/{wid}")
            assert resp.status_code == 404
        with patch("src.application.use_cases.workspace.get.index.GetWorkspace.execute", side_effect=UnauthorizedError("No")):
            resp = await client.get(f"/workspaces/{wid}")
            assert resp.status_code == 403
        with patch("src.application.use_cases.workspace.get.index.GetWorkspace.execute", side_effect=Exception("Boom")):
            resp = await client.get(f"/workspaces/{wid}")
            assert resp.status_code == 500

        # 3. List Workspaces Exceptions
        with patch("src.application.use_cases.workspace.list.index.ListWorkspaces.execute", side_effect=Exception("Boom")):
            resp = await client.get("/workspaces")
            assert resp.status_code == 500

        # 4. Update Workspace Exceptions
        with patch("src.application.use_cases.workspace.update.index.UpdateWorkspace.execute", side_effect=WorkspaceNotFoundError("Gone")):
            resp = await client.put(f"/workspaces/{wid}", json={"name": "Valid Name"})
            assert resp.status_code == 404
        with patch("src.application.use_cases.workspace.update.index.UpdateWorkspace.execute", side_effect=UnauthorizedError("No")):
            resp = await client.put(f"/workspaces/{wid}", json={"name": "Valid Name"})
            assert resp.status_code == 403
        with patch("src.application.use_cases.workspace.update.index.UpdateWorkspace.execute", side_effect=ValidationError("Bad")):
            resp = await client.put(f"/workspaces/{wid}", json={"name": "Valid Name"})
            assert resp.status_code == 400
        with patch("src.application.use_cases.workspace.update.index.UpdateWorkspace.execute", side_effect=Exception("Boom")):
            resp = await client.put(f"/workspaces/{wid}", json={"name": "Valid Name"})
            assert resp.status_code == 500

        # 5. Delete Workspace Exceptions
        with patch("src.application.use_cases.workspace.delete.index.DeleteWorkspace.execute", side_effect=WorkspaceNotFoundError("Gone")):
            resp = await client.delete(f"/workspaces/{wid}")
            assert resp.status_code == 404
        with patch("src.application.use_cases.workspace.delete.index.DeleteWorkspace.execute", side_effect=UnauthorizedError("No")):
            resp = await client.delete(f"/workspaces/{wid}")
            assert resp.status_code == 403
        with patch("src.application.use_cases.workspace.delete.index.DeleteWorkspace.execute", side_effect=Exception("Boom")):
            resp = await client.delete(f"/workspaces/{wid}")
            assert resp.status_code == 500

        # 6. Invite Member Exceptions
        with patch("src.application.use_cases.workspace.members.invite.index.InviteMember.execute", side_effect=WorkspaceNotFoundError("No WS")):
            resp = await client.post(f"/workspaces/{wid}/members", json={"email": "a@b.com", "role": "viewer"})
            assert resp.status_code == 404
        with patch("src.application.use_cases.workspace.members.invite.index.InviteMember.execute", side_effect=NotFoundError("No User")):
            resp = await client.post(f"/workspaces/{wid}/members", json={"email": "a@b.com", "role": "viewer"})
            assert resp.status_code == 404
        with patch("src.application.use_cases.workspace.members.invite.index.InviteMember.execute", side_effect=UnauthorizedError("No")):
            resp = await client.post(f"/workspaces/{wid}/members", json={"email": "a@b.com", "role": "viewer"})
            assert resp.status_code == 403
        with patch("src.application.use_cases.workspace.members.invite.index.InviteMember.execute", side_effect=ValidationError("Bad")):
            resp = await client.post(f"/workspaces/{wid}/members", json={"email": "a@b.com", "role": "viewer"})
            assert resp.status_code == 400
        with patch("src.application.use_cases.workspace.members.invite.index.InviteMember.execute", side_effect=Exception("Boom")):
            resp = await client.post(f"/workspaces/{wid}/members", json={"email": "a@b.com", "role": "viewer"})
            assert resp.status_code == 500

        # 7. List Members Exceptions
        with patch("src.application.use_cases.workspace.members.list.index.ListMembers.execute", side_effect=WorkspaceNotFoundError("Gone")):
            resp = await client.get(f"/workspaces/{wid}/members")
            assert resp.status_code == 404
        with patch("src.application.use_cases.workspace.members.list.index.ListMembers.execute", side_effect=UnauthorizedError("No")):
            resp = await client.get(f"/workspaces/{wid}/members")
            assert resp.status_code == 403
        with patch("src.application.use_cases.workspace.members.list.index.ListMembers.execute", side_effect=Exception("Boom")):
            resp = await client.get(f"/workspaces/{wid}/members")
            assert resp.status_code == 500

        # 8. Update Member Role Exceptions
        with patch("src.application.use_cases.workspace.members.update.index.UpdateMemberRole.execute", side_effect=WorkspaceNotFoundError("No WS")):
            resp = await client.put(f"/workspaces/{wid}/members/{uid}", json={"role": "editor"})
            assert resp.status_code == 404
        with patch("src.application.use_cases.workspace.members.update.index.UpdateMemberRole.execute", side_effect=MemberNotFoundError("No Mem")):
            resp = await client.put(f"/workspaces/{wid}/members/{uid}", json={"role": "editor"})
            assert resp.status_code == 404
        with patch("src.application.use_cases.workspace.members.update.index.UpdateMemberRole.execute", side_effect=UnauthorizedError("No")):
            resp = await client.put(f"/workspaces/{wid}/members/{uid}", json={"role": "editor"})
            assert resp.status_code == 403
        with patch("src.application.use_cases.workspace.members.update.index.UpdateMemberRole.execute", side_effect=ValidationError("Bad")):
            resp = await client.put(f"/workspaces/{wid}/members/{uid}", json={"role": "editor"})
            assert resp.status_code == 400
        with patch("src.application.use_cases.workspace.members.update.index.UpdateMemberRole.execute", side_effect=Exception("Boom")):
            resp = await client.put(f"/workspaces/{wid}/members/{uid}", json={"role": "editor"})
            assert resp.status_code == 500

        # 9. Remove Member Exceptions
        with patch("src.application.use_cases.workspace.members.remove.index.RemoveMember.execute", side_effect=WorkspaceNotFoundError("No WS")):
            resp = await client.delete(f"/workspaces/{wid}/members/{uid}")
            assert resp.status_code == 404
        with patch("src.application.use_cases.workspace.members.remove.index.RemoveMember.execute", side_effect=MemberNotFoundError("No Mem")):
            resp = await client.delete(f"/workspaces/{wid}/members/{uid}")
            assert resp.status_code == 404
        with patch("src.application.use_cases.workspace.members.remove.index.RemoveMember.execute", side_effect=UnauthorizedError("No")):
            resp = await client.delete(f"/workspaces/{wid}/members/{uid}")
            assert resp.status_code == 403
        with patch("src.application.use_cases.workspace.members.remove.index.RemoveMember.execute", side_effect=ValidationError("Bad")):
            resp = await client.delete(f"/workspaces/{wid}/members/{uid}")
            assert resp.status_code == 400
        with patch("src.application.use_cases.workspace.members.remove.index.RemoveMember.execute", side_effect=Exception("Boom")):
            resp = await client.delete(f"/workspaces/{wid}/members/{uid}")
            assert resp.status_code == 500

    app.dependency_overrides = {}
