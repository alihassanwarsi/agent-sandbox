from app.agent.nodes.intake import intake
from app.agent.nodes.execution import execution
from app.permissions.roles import UserRole
from app.tools.setup import build_default_registry

def test_execution_runs_permitted_tool_and_stores_result():
    registry = build_default_registry()
    state = intake("What is 2 + 2?", UserRole.VIEWER)
    state = state.model_copy(update={"selected_tool": "calculator", "tool_input": {"expression": "2 + 2"}})

    result = execution(state, registry)

    assert result.tool_result == 4

def test_execution_skips_when_permission_error_is_set():
    registry = build_default_registry()
    state = intake("Create a ticket", UserRole.VIEWER)
    state = state.model_copy(
        update={
            "selected_tool": "create_ticket",
            "tool_input": {"title": "x", "description": "y"},
            "permission_error": "blocked for testing",
        }
    )

    result = execution(state, registry)

    assert result.tool_result is None

def test_execution_skips_when_no_tool_selected():
    registry = build_default_registry()
    state = intake("Hello!", UserRole.VIEWER)

    result = execution(state, registry)

    assert result.tool_result is None

def test_execution_still_blocks_at_registry_level_as_backup():
    import pytest
    from app.permissions.checks import PermissionDenied

    registry = build_default_registry()
    state = intake("Create a ticket", UserRole.VIEWER)
    state = state.model_copy(update={"selected_tool": "create_ticket", "tool_input": {"title": "x", "description": "y"}})

    with pytest.raises(PermissionDenied):
        execution(state, registry)