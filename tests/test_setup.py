from app.tools.setup import build_default_registry

def test_default_registry_contains_all_five_tools():
    registry = build_default_registry()
    names = {tool.name for tool in registry.list_tools()}

    assert names == {
        "calculator",
        "file_reader",
        "web_search",
        "csv_reader",
        "create_ticket",
    }

def test_default_registry_tools_are_individually_retrievable():
    registry = build_default_registry()

    assert registry.get("calculator").name == "calculator"
    assert registry.get("create_ticket").name == "create_ticket"