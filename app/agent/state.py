from typing import Any, Optional
from pydantic import BaseModel
from app.permissions.roles import UserRole

class AgentState(BaseModel):
    """The shared state object passed between all pipeline nodes."""

    user_message: str
    role: UserRole

    plan: Optional[str] = None

    selected_tool: Optional[str] = None
    tool_input: Optional[dict[str, Any]] = None

    tool_result: Optional[Any] = None

    permission_error: Optional[str] = None

    final_response: Optional[str] = None