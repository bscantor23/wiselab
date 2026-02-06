import pytest
import uuid
from src.domain.budget.models import Budget
from src.domain.errors import ValidationError

def test_budget_creation_success():
    wid = uuid.uuid4()
    oid = uuid.uuid4()
    cid = uuid.uuid4()
    budget = Budget(
        workspace_id=wid,
        owner_id=oid,
        category_id=cid,
        limit_amount=500.0,
        month=1,
        year=2024
    )
    assert budget.category_id == cid
    assert budget.limit_amount == 500.0
    assert budget.month == 1
    assert budget.year == 2024

def test_budget_invalid_category():
    wid = uuid.uuid4()
    oid = uuid.uuid4()
    with pytest.raises(ValidationError, match="Category ID is required"):
        Budget(wid, oid, None, 500.0, 1, 2024)

def test_budget_invalid_limit():
    wid = uuid.uuid4()
    oid = uuid.uuid4()
    cid = uuid.uuid4()
    with pytest.raises(ValidationError, match="Limit amount must be greater than zero"):
        Budget(wid, oid, cid, 0, 1, 2024)

def test_budget_invalid_month():
    wid = uuid.uuid4()
    oid = uuid.uuid4()
    cid = uuid.uuid4()
    with pytest.raises(ValidationError, match="Month must be between 1 and 12"):
        Budget(wid, oid, cid, 500.0, 13, 2024)

def test_budget_update_limit():
    wid = uuid.uuid4()
    oid = uuid.uuid4()
    cid = uuid.uuid4()
    budget = Budget(wid, oid, cid, 500.0, 1, 2024)
    budget.update_limit(600.0)
    assert budget.limit_amount == 600.0

def test_budget_soft_delete():
    wid = uuid.uuid4()
    oid = uuid.uuid4()
    cid = uuid.uuid4()
    budget = Budget(wid, oid, cid, 500.0, 1, 2024)
    assert budget.deleted_at is None
    budget.delete()
    assert budget.deleted_at is not None
