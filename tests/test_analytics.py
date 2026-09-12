from app.approval.queue import ApprovalQueue
from app.observability.analytics import compute_safety_analytics
from app.observability.tracing import build_tracer_provider
from app.observability.trace_store import InMemoryTraceStore
from app.permissions.risk import RiskLevel
from app.permissions.roles import UserRole

def test_analytics_counts_total_runs():
    store = InMemoryTraceStore()
    provider = build_tracer_provider(exporters=[store])
    tracer = provider.get_tracer("test")

    with tracer.start_as_current_span("run_one"):
        pass
    with tracer.start_as_current_span("run_two"):
        pass

    queue = ApprovalQueue()
    analytics = compute_safety_analytics(store, queue)

    assert analytics.total_runs == 2

def test_analytics_counts_blocked_runs():
    store = InMemoryTraceStore()
    provider = build_tracer_provider(exporters=[store])
    tracer = provider.get_tracer("test")

    with tracer.start_as_current_span("blocked_run") as span:
        span.set_attribute("blocked", True)
    with tracer.start_as_current_span("normal_run"):
        pass

    queue = ApprovalQueue()
    analytics = compute_safety_analytics(store, queue)

    assert analytics.blocked_runs == 1
    assert analytics.total_runs == 2

def test_analytics_counts_confirmation_required_runs():
    store = InMemoryTraceStore()
    provider = build_tracer_provider(exporters=[store])
    tracer = provider.get_tracer("test")

    with tracer.start_as_current_span("needs_confirmation") as span:
        span.set_attribute("confirmation_required", True)

    queue = ApprovalQueue()
    analytics = compute_safety_analytics(store, queue)

    assert analytics.confirmation_required_runs == 1

def test_analytics_counts_approval_queue_outcomes():
    store = InMemoryTraceStore()
    queue = ApprovalQueue()

    request_one = queue.submit(
        tool_name="create_ticket",
        tool_input={"title": "a", "description": "b"},
        risk_level=RiskLevel.HIGH,
        role=UserRole.OPERATOR,
        reasoning="test",
        thread_id="test-thread"
    )
    queue.approve(request_one.id, decided_by="alice")

    request_two = queue.submit(
        tool_name="create_ticket",
        tool_input={"title": "c", "description": "d"},
        risk_level=RiskLevel.HIGH,
        role=UserRole.OPERATOR,
        reasoning="test",
        thread_id="test-thread"
    )
    queue.reject(request_two.id, decided_by="alice", reason="no")

    queue.submit(
        tool_name="create_ticket",
        tool_input={"title": "e", "description": "f"},
        risk_level=RiskLevel.HIGH,
        role=UserRole.OPERATOR,
        reasoning="test",
        thread_id="test-thread"
    )

    analytics = compute_safety_analytics(store, queue)

    assert analytics.approved_requests == 1
    assert analytics.rejected_requests == 1
    assert analytics.pending_approvals == 1
    assert analytics.modified_requests == 0