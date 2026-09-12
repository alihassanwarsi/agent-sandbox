from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field
from app.permissions.risk import RiskLevel
from app.permissions.roles import UserRole

class ApprovalStatus(str, Enum):
    """The current state of an approval request."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"

class ApprovalRequest(BaseModel):
    """One request sitting in the approval queue."""

    id: str = Field(..., description="A unique identifier for this approval request.")
    tool_name: str
    tool_input: dict[str, Any]
    risk_level: RiskLevel
    role: UserRole
    thread_id: str = Field(..., description="The LangGraph run this approval request belongs to.")
    reasoning: str = Field(..., description="The model's reasoning for proposing this action.")
    status: ApprovalStatus = ApprovalStatus.PENDING

    decided_by: Optional[str] = None
    decision_reason: Optional[str] = None

    final_tool_input: Optional[dict[str, Any]] = None
