from pydantic import BaseModel
from app.approval.models import ApprovalStatus
from app.approval.queue import ApprovalQueue
from app.observability.trace_store import InMemoryTraceStore

class SafetyAnalytics(BaseModel):
    """A snapshot of how requests have been handled so far."""

    total_runs: int
    blocked_runs: int
    confirmation_required_runs: int

    pending_approvals: int
    approved_requests: int
    rejected_requests: int
    modified_requests: int


def _trace_had_attribute(spans: list, attribute: str) -> bool:
    """Check if any span in a trace has a given attribute set to True."""

    for span in spans:
        attributes = dict(span.attributes or {})
        if attributes.get(attribute):
            return True
    return False


def compute_safety_analytics(trace_store: InMemoryTraceStore, queue: ApprovalQueue) -> SafetyAnalytics:
    """Compute a summary of system activity from the trace store and approval queue."""

    trace_ids = trace_store.list_trace_ids()
    total_runs = len(trace_ids)

    blocked_runs = 0
    confirmation_required_runs = 0

    for trace_id in trace_ids:
        spans = trace_store.get_trace(trace_id)
        if _trace_had_attribute(spans, "blocked"):
            blocked_runs += 1
        if _trace_had_attribute(spans, "confirmation_required"):
            confirmation_required_runs += 1

    all_requests = queue.list_all()

    return SafetyAnalytics(
        total_runs=total_runs,
        blocked_runs=blocked_runs,
        confirmation_required_runs=confirmation_required_runs,
        pending_approvals=sum(1 for r in all_requests if r.status == ApprovalStatus.PENDING),
        approved_requests=sum(1 for r in all_requests if r.status == ApprovalStatus.APPROVED),
        rejected_requests=sum(1 for r in all_requests if r.status == ApprovalStatus.REJECTED),
        modified_requests=sum(1 for r in all_requests if r.status == ApprovalStatus.MODIFIED),
    )