from datetime import datetime, timezone
import uuid
import time
from src.domain.auth.models import User
from src.domain.auth.value_objects import Email
from src.domain.base import Entity

def test_user_creation_and_properties():
    """Test user initialization and property accessors"""
    email = Email("test@example.com")
    user = User(email=email, password_hash="hash")
    
    assert user.email == email
    assert user.password_hash == "hash"
    assert user.is_active is True
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)

def test_user_activation_lifecycle():
    """Test deactivate and activate methods"""
    email = Email("test@example.com")
    user = User(email=email, password_hash="hash")
    
    user.deactivate()
    assert user.is_active is False
    
    user.activate()
    assert user.is_active is True

def test_user_update_profile():
    """Test update_profile method logic"""
    email = Email("test@example.com")
    user = User(email=email, password_hash="hash")
    original_updated_at = user.updated_at
    
    # Ensure time passes
    time.sleep(0.001)
    
    # Update with name
    user.update_profile(full_name="New Name")
    assert user.full_name == "New Name"
    assert user.updated_at > original_updated_at
    
    # Update without name (should just update timestamp)
    mid_updated_at = user.updated_at
    time.sleep(0.001)
    user.update_profile(full_name=None)
    assert user.full_name == "New Name" # Should not change
    assert user.updated_at > mid_updated_at

def test_entity_equality_and_id():
    """Test base Entity equality and hashing"""
    id1 = uuid.uuid4()
    e1 = Entity(id1)
    e2 = Entity(id1)
    e3 = Entity(uuid.uuid4())
    
    assert e1 == e2
    assert e1 != e3
    assert e1 != "not-an-entity"
    assert hash(e1) == hash(id1)

def test_entity_default_timestamps():
    """Test that timestamps are generated if not provided"""
    e = Entity()
    assert isinstance(e.created_at, datetime)
    assert isinstance(e.updated_at, datetime)

def test_email_value_object_equality():
    e1 = Email("a@b.com")
    e2 = Email("c@d.com")
    e3 = Email("a@b.com")
    
    assert e1 != e2
    assert e1 == e3
    assert e1 != "not-an-email"
