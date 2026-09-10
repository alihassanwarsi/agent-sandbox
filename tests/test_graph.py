from app.agent.graph import build_graph
from app.tools.setup import build_default_registry
from app.agent.graph import build_graph, run_agent
from app.permissions.roles import UserRole

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

def test_high_risk_tool_routes_to_approval_wait():
    registry = build_default_registry()

    def fake_llm(prompt: str) -> str:
        return '{"tool": "create_ticket", "input": {"title": "x", "description": "y"}, "reasoning": "test"}'

    from app.agent.nodes.intake import intake
    from app.agent.nodes.plan import plan
    from app.agent.nodes.permission_check import permission_check

    state = intake("Create a ticket for a server outage", UserRole.OPERATOR)
    state = plan(state, registry, llm_call=fake_llm)
    state = permission_check(state)

    compiled = build_graph(registry)
    result_dict = compiled.invoke(state)

    assert result_dict["awaiting_approval"] is True
    assert "requires human approval" in result_dict["final_response"]