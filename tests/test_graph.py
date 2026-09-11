from app.agent.graph import build_graph, run_agent, resume_agent
from app.agent.nodes.intake import intake
from app.approval.queue import ApprovalQueue
from app.permissions.roles import UserRole
from app.tools.setup import build_default_registry

def fake_llm_calculator_choice(prompt: str) -> str:
    return '{"tool": "calculator", "input": {"expression": "2 + 2"}, "reasoning": "Math question."}'

def fake_llm_ticket_choice(prompt: str) -> str:
    return '{"tool": "create_ticket", "input": {"title": "Server down", "description": "Prod is offline"}, "reasoning": "User reported an outage."}'

def test_graph_compiles_successfully():
    registry = build_default_registry()
    queue = ApprovalQueue()
    compiled = build_graph(registry, queue)
    assert compiled is not None

def test_graph_has_all_expected_nodes():
    registry = build_default_registry()
    queue = ApprovalQueue()
    compiled = build_graph(registry, queue)

    node_names = set(compiled.get_graph().nodes.keys())
    expected = {"plan", "permission_check", "execution", "reflection", "approval_wait", "__start__", "__end__"}
    assert expected.issubset(node_names)

def test_low_risk_request_completes_immediately():
    registry = build_default_registry()
    queue = ApprovalQueue()

    state = intake("What is 2 + 2?", UserRole.VIEWER)

    compiled = build_graph(registry, queue, llm_call=fake_llm_calculator_choice)
    result = compiled.invoke(state, config={"configurable": {"thread_id": "test-thread-1"}})

    assert "__interrupt__" not in result
    assert result["tool_result"] == 4

def test_high_risk_request_pauses_and_submits_to_queue():
    registry = build_default_registry()
    queue = ApprovalQueue()

    state = intake("Create a ticket for a server outage", UserRole.OPERATOR)

    compiled = build_graph(registry, queue, llm_call=fake_llm_ticket_choice)
    result = compiled.invoke(state, config={"configurable": {"thread_id": "test-thread-2"}})

    assert "__interrupt__" in result
    assert len(queue.list_pending()) == 1

def test_resume_after_approval_runs_the_tool():
    registry = build_default_registry()
    queue = ApprovalQueue()

    state = intake("Create a ticket for a server outage", UserRole.OPERATOR)

    compiled = build_graph(registry, queue, llm_call=fake_llm_ticket_choice)
    thread_id = "test-thread-3"
    compiled.invoke(state, config={"configurable": {"thread_id": thread_id}})

    pending = queue.list_pending()[0]
    queue.approve(pending.id, decided_by="alice")

    result = resume_agent(
        thread_id,
        {"outcome": "approved", "tool_input": pending.tool_input},
        registry,
        queue,
        llm_call=fake_llm_ticket_choice,
    )

    assert result["status"] == "completed"
    assert result["state"].tool_result is not None

def test_resume_after_rejection_does_not_run_the_tool():
    registry = build_default_registry()
    queue = ApprovalQueue()

    state = intake("Create a ticket for a server outage", UserRole.OPERATOR)

    compiled = build_graph(registry, queue, llm_call=fake_llm_ticket_choice)
    thread_id = "test-thread-4"
    compiled.invoke(state, config={"configurable": {"thread_id": thread_id}})

    pending = queue.list_pending()[0]
    queue.reject(pending.id, decided_by="alice", reason="Not urgent enough.")

    result = resume_agent(
        thread_id,
        {"outcome": "rejected", "reason": "Not urgent enough."},
        registry,
        queue,
        llm_call=fake_llm_ticket_choice,
    )

    assert result["status"] == "completed"
    assert result["state"].tool_result is None
    assert "rejected" in result["state"].final_response.lower()