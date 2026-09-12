import pytest
from app.db.database import Base, engine, get_db_session
from app.db.models import ApprovalRequestORM
from app.db.postgres_queue import PostgresApprovalQueue
from app.permissions.risk import RiskLevel
from app.permissions.roles import UserRole

@pytest.fixture(autouse=True)
def clean_table():
    """Wipe the table before and after each test, so tests don't interfere with each other."""
    session = get_db_session()
    session.query(ApprovalRequestORM).delete()
    session.commit()
    session.close()
    yield
    session = get_db_session()
    session.query(ApprovalRequestORM).delete()
    session.commit()
    session.close()

def test_submit_creates_a_pending_row():
    queue = PostgresApprovalQueue()
    request = queue.submit(
        tool_name="create_ticket",
        tool_input={"title": "x", "description": "y"},
        risk_level=RiskLevel.HIGH,
        role=UserRole.OPERATOR,
        reasoning="test",
        thread_id="test-thread",
    )

    assert request.status.value == "pending"
    fetched = queue.get(request.id)
    assert fetched.tool_name == "create_ticket"

def test_list_pending_returns_only_pending():
    queue = PostgresApprovalQueue()
    request = queue.submit(
        tool_name="create_ticket",
        tool_input={"title": "x", "description": "y"},
        risk_level=RiskLevel.HIGH,
        role=UserRole.OPERATOR,
        reasoning="test",
        thread_id="test-thread",
    )

    pending = queue.list_pending()
    assert len(pending) == 1
    assert pending[0].id == request.id

def test_approve_updates_the_row():
    queue = PostgresApprovalQueue()
    request = queue.submit(
        tool_name="create_ticket",
        tool_input={"title": "x", "description": "y"},
        risk_level=RiskLevel.HIGH,
        role=UserRole.OPERATOR,
        reasoning="test",
        thread_id="test-thread",
    )

    approved = queue.approve(request.id, decided_by="alice")

    assert approved.status.value == "approved"
    assert approved.decided_by == "alice"
    assert queue.list_pending() == []

def test_reject_updates_the_row():
    queue = PostgresApprovalQueue()
    request = queue.submit(
        tool_name="create_ticket",
        tool_input={"title": "x", "description": "y"},
        risk_level=RiskLevel.HIGH,
        role=UserRole.OPERATOR,
        reasoning="test",
        thread_id="test-thread",
    )

    rejected = queue.reject(request.id, decided_by="alice", reason="no")

    assert rejected.status.value == "rejected"
    assert rejected.decision_reason == "no"

def test_find_pending_for_finds_a_match():
    queue = PostgresApprovalQueue()
    request = queue.submit(
        tool_name="create_ticket",
        tool_input={"title": "x", "description": "y"},
        risk_level=RiskLevel.HIGH,
        role=UserRole.OPERATOR,
        reasoning="test",
        thread_id="test-thread",
    )

    found = queue.find_pending_for("create_ticket", {"title": "x", "description": "y"}, UserRole.OPERATOR)
    assert found.id == request.id

def test_getting_unknown_id_raises_error():
    queue = PostgresApprovalQueue()
    with pytest.raises(KeyError):
        queue.get("does-not-exist")