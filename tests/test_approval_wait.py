from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from app.agent.nodes.approval_wait import approval_wait
from app.agent.nodes.intake import intake
from app.agent.state import AgentState
from app.approval.queue import ApprovalQueue
from app.permissions.roles import UserRole
from app.permissions.risk import TOOL_RISK_LEVELS

def make_sample_request(queue):
    return queue.submit(
        tool_name="create_ticket",
        tool_input={"title": "Server down", "description": "Prod is offline"},
        risk_level=TOOL_RISK_LEVELS["create_ticket"],
        role=UserRole.OPERATOR,
        reasoning="",
        thread_id="test-thread",
    )

def test_approval_wait_submits_to_queue_and_pauses():
    queue = ApprovalQueue()
    state = intake("Create a ticket", UserRole.OPERATOR)
    state = state.model_copy(update={"selected_tool": "create_ticket", "tool_input": {"title": "x", "description": "y"}})

    def approval_wait_node(state: AgentState) -> dict:
        return approval_wait(state, queue, "test-thread").model_dump()

    graph = StateGraph(AgentState)
    graph.add_node("approval_wait", approval_wait_node)
    graph.add_edge(START, "approval_wait")
    graph.add_edge("approval_wait", END)

    compiled = graph.compile(checkpointer=MemorySaver())

    result = compiled.invoke(
        state,
        config={"configurable": {"thread_id": "test-approval-wait"}}
    )

    assert "__interrupt__" in result
    assert len(queue.list_pending()) == 1

def test_find_pending_for_returns_matching_request():
    queue = ApprovalQueue()
    request = make_sample_request(queue)

    found = queue.find_pending_for(
        tool_name="create_ticket",
        tool_input={"title": "Server down", "description": "Prod is offline"},
        role=UserRole.OPERATOR,
    )

    assert found.id == request.id

def test_find_pending_for_returns_none_when_no_match():
    queue = ApprovalQueue()
    make_sample_request(queue)

    found = queue.find_pending_for(
        tool_name="create_ticket",
        tool_input={"title": "Different ticket", "description": "Different issue"},
        role=UserRole.OPERATOR,
    )

    assert found is None
    
def test_find_pending_for_ignores_already_resolved_requests():
    queue = ApprovalQueue()
    request = make_sample_request(queue)
    queue.approve(request.id, decided_by="alice")

    found = queue.find_pending_for(
        tool_name="create_ticket",
        tool_input={"title": "Server down", "description": "Prod is offline"},
        role=UserRole.OPERATOR,
    )

    assert found is None