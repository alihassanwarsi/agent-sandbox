import pytest
from app.agent.nodes.intake import intake
from app.permissions.roles import UserRole

def test_intake_builds_state_with_message_and_role():
    state = intake("Create a ticket for this bug", UserRole.OPERATOR)

    assert state.user_message == "Create a ticket for this bug"
    assert state.role == UserRole.OPERATOR

def test_intake_rejects_empty_message():
    with pytest.raises(ValueError):
        intake("", UserRole.VIEWER)

def test_intake_state_starts_with_no_plan_or_result():
    state = intake("Hello", UserRole.VIEWER)

    assert state.plan is None
    assert state.selected_tool is None
    assert state.tool_result is None
    assert state.final_response is None