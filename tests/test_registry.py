import pytest
from pydantic import BaseModel
from app.tools.registry import Tool, ToolRegistry
from app.permissions.checks import PermissionDenied
from app.permissions.roles import UserRole

class DummyInput(BaseModel):
    text: str

def dummy_handler(data: DummyInput) -> str:
    return data.text.upper()

def make_dummy_tool(name: str = "dummy_tool") -> Tool:
    return Tool(
        name=name,
        description="A tool used only for testing.",
        input_schema=DummyInput,
        handler=dummy_handler,
    )

def test_register_and_get_tool():
    registry = ToolRegistry()
    tool = make_dummy_tool()

    registry.register(tool)
    fetched = registry.get("dummy_tool")

    assert fetched.name == "dummy_tool"
    assert fetched.description == "A tool used only for testing."

def test_registering_duplicate_name_raises_error():
    registry = ToolRegistry()
    registry.register(make_dummy_tool())

    with pytest.raises(ValueError):
        registry.register(make_dummy_tool())

def test_getting_unknown_tool_raises_error():
    registry = ToolRegistry()

    with pytest.raises(KeyError):
        registry.get("does_not_exist")

def test_list_tools_returns_all_registered_tools():
    registry = ToolRegistry()
    registry.register(make_dummy_tool("tool_one"))
    registry.register(make_dummy_tool("tool_two"))

    names = {tool.name for tool in registry.list_tools()}
    assert names == {"tool_one", "tool_two"}

def test_tool_handler_actually_runs():
    tool = make_dummy_tool()
    result = tool.handler(DummyInput(text="hello"))
    assert result == "HELLO"

def test_run_executes_tool_when_role_is_permitted():
    from app.tools.setup import build_default_registry

    registry = build_default_registry()
    result = registry.run(
        "calculator",
        UserRole.VIEWER,
        registry.get("calculator").input_schema(expression="2 + 2"),
    )
    assert result == 4

def test_run_blocks_tool_when_role_is_not_permitted():
    from app.tools.setup import build_default_registry

    registry = build_default_registry()

    with pytest.raises(PermissionDenied):
        registry.run(
            "create_ticket",
            UserRole.VIEWER,
            registry.get("create_ticket").input_schema(title="x", description="y"),
        )