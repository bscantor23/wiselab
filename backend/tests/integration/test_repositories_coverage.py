import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.auth.repositories import SQLUserRepository
from src.domain.auth.models import User
from src.domain.auth.value_objects import Email

@pytest.mark.asyncio
async def test_repository_full_coverage(db_session: AsyncSession):
    repo = SQLUserRepository(db_session)
    
    # Setup
    email = Email("repo@example.com")
    user = User(email=email, password_hash="hash", full_name="Repo User")
    await repo.add(user)
    await db_session.commit()
    
    # Test get_by_id
    found_by_id = await repo.get_by_id(user.id)
    assert found_by_id is not None
    assert found_by_id.email == email
    
    # Test get_by_id not found
    assert await repo.get_by_id(uuid.uuid4()) is None
    
    # Test get_by_email not found
    assert await repo.get_by_email(Email("not@found.com")) is None
    
    # Test list
    users = await repo.list()
    assert len(users) >= 1
    assert any(u.email == email for u in users)
    
    # Test remove
    await repo.remove(user)
    await db_session.commit()
    assert await repo.get_by_id(user.id) is None
    
    # Test remove not found (should not raise)
    await repo.remove(user)
