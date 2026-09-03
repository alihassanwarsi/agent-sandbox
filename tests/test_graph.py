from app.agent.graph import build_graph
from app.tools.setup import build_default_registry

def test_graph_compiles_successfully():
    registry = build_default_registry()
    compiled = build_graph(registry)
    assert compiled is not None

def test_graph_has_all_expected_nodes():
    registry = build_default_registry()
    compiled = build_graph(registry)

    node_names = set(compiled.get_graph().nodes.keys())
    expected = {"plan", "permission_check", "execution", "reflection", "__start__", "__end__"}
    assert expected.issubset(node_names)