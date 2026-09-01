import pytest
from app.agent.nodes.intake import intake
from app.agent.nodes.plan import plan
from app.permissions.roles import UserRole
from app.tools.setup import build_default_registry

def fake_llm_calculator_choice(prompt: str) -> str:
    """Pretends the LLM chose the calculator tool."""
    return '{"tool": "calculator", "input": {"expression": "2 + 2"}, "reasoning": "Math question."}'

def fake_llm_no_tool_choice(prompt: str) -> str:
    """Pretends the LLM decided no tool is needed."""
    return '{"tool": null, "input": {}, "reasoning": "Just a greeting, no tool needed."}'

def fake_llm_invalid_tool_choice(prompt: str) -> str:
    """Pretends the LLM hallucinated a tool that does not exist."""
    return '{"tool": "not_a_real_tool", "input": {}, "reasoning": "Oops."}'

def fake_llm_broken_json(prompt: str) -> str:
    """Pretends the LLM returned something that is not valid JSON."""
    return "this is not json"

def test_plan_selects_a_known_tool():
    registry = build_default_registry()
    state = intake("What is 2 + 2?", UserRole.VIEWER)

    updated_state = plan(state, registry, llm_call=fake_llm_calculator_choice)

    assert updated_state.selected_tool == "calculator"
    assert updated_state.tool_input == {"expression": "2 + 2"}
    assert updated_state.plan == "Math question."

def test_plan_allows_no_tool_selection():
    registry = build_default_registry()
    state = intake("Hi there!", UserRole.VIEWER)

    updated_state = plan(state, registry, llm_call=fake_llm_no_tool_choice)

    assert updated_state.selected_tool is None

def test_plan_rejects_unknown_tool_choice():
    registry = build_default_registry()
    state = intake("Do something weird", UserRole.VIEWER)

    with pytest.raises(ValueError):
        plan(state, registry, llm_call=fake_llm_invalid_tool_choice)

def test_plan_rejects_non_json_response():
    registry = build_default_registry()
    state = intake("Do something", UserRole.VIEWER)

    with pytest.raises(ValueError):
        plan(state, registry, llm_call=fake_llm_broken_json)

def test_plan_preserves_original_state_fields():
    registry = build_default_registry()
    state = intake("What is 2 + 2?", UserRole.OPERATOR)

    updated_state = plan(state, registry, llm_call=fake_llm_calculator_choice)

    assert updated_state.user_message == "What is 2 + 2?"
    assert updated_state.role == UserRole.OPERATOR