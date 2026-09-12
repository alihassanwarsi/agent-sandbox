import uuid
from typing import Optional
from app.permissions.roles import UserRole
from app.permissions.risk import RiskLevel
from app.approval.models import ApprovalRequest, ApprovalStatus

class ApprovalQueue:
    """Holds pending, approved, rejected, and modified approval requests."""

    def __init__(self):
        self._requests: dict[str, ApprovalRequest] = {}

    def submit(self, tool_name: str, tool_input: dict, risk_level: RiskLevel, role: UserRole, reasoning: str, thread_id: str) -> ApprovalRequest:
        """Add a new pending request to the queue and return it."""

        request = ApprovalRequest(
            id=str(uuid.uuid4()),
            tool_name=tool_name,
            tool_input=tool_input,
            risk_level=risk_level,
            role=role,
            reasoning=reasoning,
            thread_id=thread_id,
        )
        self._requests[request.id] = request
        return request

    def get(self, request_id: str) -> ApprovalRequest:
        """Fetch a request by its id."""

        if request_id not in self._requests:
            raise KeyError(f"No approval request found with id '{request_id}'.")
        return self._requests[request_id]

    def list_pending(self) -> list[ApprovalRequest]:
        """Return all requests still waiting for a decision."""

        return [req for req in self._requests.values() if req.status == ApprovalStatus.PENDING]

    def list_all(self) -> list[ApprovalRequest]:
        """Return every request ever submitted, regardless of status."""
        return list(self._requests.values())

    def find_pending_for(self, tool_name: str, tool_input: dict, role: UserRole) -> Optional[ApprovalRequest]:
        """Find a matching PENDING request to avoid duplicates on resume."""

        for request in self._requests.values():
            if (
                request.status == ApprovalStatus.PENDING
                and request.tool_name == tool_name
                and request.tool_input == tool_input
                and request.role == role
            ):
                return request
        return None

    def approve(self, request_id: str, decided_by: str) -> ApprovalRequest:
        """Approve a request"""

        request = self.get(request_id)
        request.status = ApprovalStatus.APPROVED
        request.decided_by = decided_by
        request.final_tool_input = request.tool_input
        return request

    def reject(self, request_id: str, decided_by: str, reason: str) -> ApprovalRequest:
        """Reject a request"""

        request = self.get(request_id)
        request.status = ApprovalStatus.REJECTED
        request.decided_by = decided_by
        request.decision_reason = reason
        return request

    def modify(self, request_id: str, decided_by: str, new_tool_input: dict, reason: str) -> ApprovalRequest:
        """Approve a request, but with corrected/edited arguments."""

        request = self.get(request_id)
        request.status = ApprovalStatus.MODIFIED
        request.decided_by = decided_by
        request.decision_reason = reason
        request.final_tool_input = new_tool_input
        return request
