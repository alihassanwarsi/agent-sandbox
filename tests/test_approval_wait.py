from app.agent.nodes.approval_wait import approval_wait
from app.agent.nodes.intake import intake
from app.permissions.roles import UserRole


def test_approval_wait_marks_state_as_awaiting_approval():
    state = intake("Create a ticket", UserRole.OPERATOR)
    state = state.model_copy(update={"selected_tool": "create_ticket"})

    result = approval_wait(state)

    assert result.awaiting_approval is True
    assert "requires human approval" in result.final_response