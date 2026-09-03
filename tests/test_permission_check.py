from app.agent.nodes.intake import intake
from app.agent.nodes.permission_check import permission_check
from app.permissions.roles import UserRole

def test_allowed_tool_passes_through_with_no_error():
    state = intake("What is 2 + 2?", UserRole.VIEWER)
    state = state.model_copy(update={"selected_tool": "calculator", "tool_input": {"expression": "2 + 2"}})

    result = permission_check(state)

    assert result.permission_error is None
    assert result.selected_tool == "calculator"

def test_blocked_tool_sets_permission_error():
    state = intake("Create a ticket", UserRole.VIEWER)
    state = state.model_copy(update={"selected_tool": "create_ticket", "tool_input": {"title": "x", "description": "y"}})

    result = permission_check(state)

    assert result.permission_error is not None
    assert "VIEWER" in result.permission_error

def test_no_tool_selected_passes_through_unchanged():
    state = intake("Hello!", UserRole.VIEWER)

    result = permission_check(state)

    assert result.permission_error is None
    assert result.selected_tool is None

def test_operator_passes_permission_check_for_high_risk_tool():
    state = intake("Create a ticket", UserRole.OPERATOR)
    state = state.model_copy(update={"selected_tool": "create_ticket", "tool_input": {"title": "x", "description": "y"}})

    result = permission_check(state)

    assert result.permission_error is None