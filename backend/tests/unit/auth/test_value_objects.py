import pytest
from src.domain.auth.value_objects import Email
from src.domain.errors import ValidationError

def test_email_validation_success():
    email = Email("test@example.com")
    assert email.value == "test@example.com"

def test_email_validation_failure():
    with pytest.raises(ValidationError, match="Invalid email format"):
        Email("invalid-email")

def test_email_equality():
    e1 = Email("a@b.com")
    e2 = Email("c@d.com") 
    e3 = Email("a@b.com")
    
    assert e1 == e3
    assert e1 != e2
    assert e1 != "string"
