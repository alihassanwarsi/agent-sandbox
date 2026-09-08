import pytest
from app.approval.models import ApprovalStatus
from app.approval.queue import ApprovalQueue
from app.permissions.risk import RiskLevel
from app.permissions.roles import UserRole

def make_sample_request(queue: ApprovalQueue):
    return queue.submit(
        tool_name="create_ticket",
        tool_input={"title": "Server down", "description": "Prod is offline"},
        risk_level=RiskLevel.HIGH,
        role=UserRole.OPERATOR,
        reasoning="User reported a critical outage.",
    )

def test_submit_creates_a_pending_request():
    queue = ApprovalQueue()
    request = make_sample_request(queue)

    assert request.status == ApprovalStatus.PENDING
    assert request.tool_name == "create_ticket"

def test_list_pending_returns_only_pending_requests():
    queue = ApprovalQueue()
    request = make_sample_request(queue)

    pending = queue.list_pending()
    assert len(pending) == 1
    assert pending[0].id == request.id

def test_approve_sets_status_and_final_input():
    queue = ApprovalQueue()
    request = make_sample_request(queue)

    approved = queue.approve(request.id, decided_by="alice")

    assert approved.status == ApprovalStatus.APPROVED
    assert approved.decided_by == "alice"
    assert approved.final_tool_input == request.tool_input
    assert queue.list_pending() == []  # no longer pending

def test_reject_sets_status_and_reason():
    queue = ApprovalQueue()
    request = make_sample_request(queue)

    rejected = queue.reject(request.id, decided_by="alice", reason="Not a real emergency.")

    assert rejected.status == ApprovalStatus.REJECTED
    assert rejected.decision_reason == "Not a real emergency."

def test_modify_sets_status_and_new_input():
    queue = ApprovalQueue()
    request = make_sample_request(queue)

    modified = queue.modify(
        request.id,
        decided_by="alice",
        new_tool_input={"title": "Corrected title", "description": "Prod is offline"},
        reason="Fixed vague title.",
    )

    assert modified.status == ApprovalStatus.MODIFIED
    assert modified.final_tool_input["title"] == "Corrected title"

def test_getting_unknown_request_raises_error():
    queue = ApprovalQueue()
    with pytest.raises(KeyError):
        queue.get("does-not-exist")