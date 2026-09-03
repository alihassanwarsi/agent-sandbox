from app.agent.nodes.intake import intake
from app.agent.nodes.reflection import reflection
from app.permissions.roles import UserRole


def fake_llm_explains_result(prompt: str) -> str:
    return "The answer is 4."

def fake_llm_direct_answer(prompt: str) -> str:
    return "Hello! How can I help you today?"

def test_reflection_returns_deterministic_message_when_blocked():
    state = intake("Create a ticket", UserRole.VIEWER)
    state = state.model_copy(update={"permission_error": "Role 'VIEWER' is not permitted to use tool 'create_ticket'."})

    result = reflection(state, llm_call=fake_llm_explains_result)

    assert "not able to complete" in result.final_response
    assert "VIEWER" in result.final_response

def test_reflection_uses_llm_to_explain_tool_result():
    state = intake("What is 2 + 2?", UserRole.VIEWER)
    state = state.model_copy(update={"selected_tool": "calculator", "tool_result": 4})

    result = reflection(state, llm_call=fake_llm_explains_result)

    assert result.final_response == "The answer is 4."

def test_reflection_uses_llm_for_direct_answer_when_no_tool_used():
    state = intake("Hi there!", UserRole.VIEWER)

    result = reflection(state, llm_call=fake_llm_direct_answer)

    assert result.final_response == "Hello! How can I help you today?"

def test_permission_error_takes_priority_over_tool_result():
    state = intake("Create a ticket", UserRole.VIEWER)
    state = state.model_copy(
        update={
            "permission_error": "blocked",
            "tool_result": "should not matter",
        }
    )

    result = reflection(state, llm_call=fake_llm_explains_result)

    assert "not able to complete" in result.final_response