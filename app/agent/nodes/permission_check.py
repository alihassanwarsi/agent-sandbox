from app.agent.state import AgentState
from app.permissions.checks import PermissionDenied, check_permission

def permission_check(state: AgentState) -> AgentState:
    """Check permission for the selected tool, if any, and update state."""

    if state.selected_tool is None:
        return state  
    try:
        check_permission(state.role, state.selected_tool)
    except PermissionDenied as exc:
        return state.model_copy(update={"permission_error": str(exc)})
    return state

