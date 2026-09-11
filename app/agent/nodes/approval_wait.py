from langgraph.types import interrupt
from app.agent.state import AgentState
from app.approval.queue import ApprovalQueue
from app.permissions.risk import TOOL_RISK_LEVELS


def approval_wait(state: AgentState, queue: ApprovalQueue) -> AgentState:
    """Submit the request for approval (or reuse an existing pending one), then pause."""

    tool_input = state.tool_input or {}

    approval_request = queue.find_pending_for(state.selected_tool, tool_input, state.role)
    if approval_request is None:
        approval_request = queue.submit(
            tool_name=state.selected_tool,
            tool_input=tool_input,
            risk_level=TOOL_RISK_LEVELS[state.selected_tool],
            role=state.role,
            reasoning=state.plan or "",
        )

    decision = interrupt(
        {
            "approval_request_id": approval_request.id,
            "tool_name": approval_request.tool_name,
            "tool_input": approval_request.tool_input,
            "reasoning": approval_request.reasoning,
        }
    )

    if decision["outcome"] == "rejected":
        return state.model_copy(
            update={
                "permission_error": f"Request was rejected by a human reviewer: {decision.get('reason', '')}",
                "awaiting_approval": False,
            }
        )

    final_input = decision.get("tool_input", state.tool_input)

    return state.model_copy(
        update={
            "tool_input": final_input,
            "confirmed": True,
            "awaiting_approval": False,
        }
    )