from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from app.agent.nodes.intake import intake
from app.agent.nodes.plan import plan
from app.agent.nodes.permission_check import permission_check
from app.agent.nodes.execution import execution
from app.agent.nodes.reflection import reflection
from app.agent.state import AgentState
from app.agent.llm import call_llm
from app.permissions.roles import UserRole
from app.tools.registry import ToolRegistry
from app.agent.nodes.approval_wait import approval_wait
from app.permissions.risk import RiskLevel, TOOL_RISK_LEVELS
from app.approval.queue import ApprovalQueue
from app.observability.tracing import build_tracer_provider
from app.observability.trace_node import traced_node
from app.observability.trace_store import InMemoryTraceStore
from opentelemetry.sdk.trace.export import ConsoleSpanExporter

_checkpointer = MemorySaver()

_trace_store = InMemoryTraceStore()
_tracer_provider = build_tracer_provider(exporters=[ConsoleSpanExporter(), _trace_store])
_tracer = _tracer_provider.get_tracer("agent_sandbox")

def _route_after_permission_check(state: AgentState) -> str:
    """Decide the next step after permission check."""

    if state.permission_error is not None:
        return "reflection"

    if state.selected_tool is None:
        return "execution"

    risk = TOOL_RISK_LEVELS[state.selected_tool]

    if risk == RiskLevel.HIGH:
        return "approval_wait"

    return "execution"

def _route_after_approval_wait(state: AgentState) -> str:
    """Route to Reflection if rejected, otherwise to Execution."""

    if state.permission_error is not None:
        return "reflection"

    return "execution"

def build_graph(registry: ToolRegistry, queue: ApprovalQueue, llm_call=call_llm):
    """Build and compile the LangGraph pipeline, bound to the given tool registry and approval queue."""

    def plan_node(state: AgentState) -> dict:
        return plan(state, registry, llm_call=llm_call).model_dump()

    def permission_check_node(state: AgentState) -> dict:
        return permission_check(state).model_dump()

    def execution_node(state: AgentState) -> dict:
        return execution(state, registry).model_dump()

    def reflection_node(state: AgentState) -> dict:
        return reflection(state, llm_call=llm_call).model_dump()

    def approval_wait_node(state: AgentState) -> dict:
        return approval_wait(state, queue).model_dump()

    graph = StateGraph(AgentState)

    graph.add_node("plan", traced_node(_tracer, "plan", plan_node))
    graph.add_node("permission_check", traced_node(_tracer, "permission_check", permission_check_node))
    graph.add_node("execution", traced_node(_tracer, "execution", execution_node))
    graph.add_node("reflection", traced_node(_tracer, "reflection", reflection_node))
    graph.add_node("approval_wait", traced_node(_tracer, "approval_wait", approval_wait_node))

    graph.add_edge(START, "plan")
    graph.add_edge("plan", "permission_check")
    graph.add_conditional_edges(
        "permission_check", _route_after_permission_check, {
            "reflection": "reflection",
            "execution": "execution",
            "approval_wait": "approval_wait"
        }
    )
    graph.add_edge("execution", "reflection")
    graph.add_conditional_edges(
        "approval_wait", _route_after_approval_wait, {
            "reflection": "reflection",
            "execution": "execution"
        }
    )
    graph.add_edge("reflection", END)

    return graph.compile(checkpointer=_checkpointer)

def run_agent(user_message: str, role: UserRole, registry: ToolRegistry, queue: ApprovalQueue, thread_id: str, llm_call=call_llm) -> dict:
    """Run the full pipeline for one request, returning the final AgentState."""

    with _tracer.start_as_current_span("agent_run") as run_span:
        run_span.set_attribute("thread_id", thread_id)
        run_span.set_attribute("role", role.name)

        initial_state = intake(user_message, role)
        compiled_graph = build_graph(registry, queue, llm_call=llm_call)

        config = {"configurable": {"thread_id": thread_id}}
        result = compiled_graph.invoke(initial_state, config=config)

        if "__interrupt__" in result:
            interrupt_data = result["__interrupt__"][0].value
            run_span.set_attribute("awaiting_approval", True)
            return {"status": "awaiting_approval", "approval_request_id": interrupt_data["approval_request_id"]}

        return {"status": "completed", "state": AgentState(**result)}

def resume_agent(thread_id: str, decision: dict, registry: ToolRegistry, queue: ApprovalQueue, llm_call=call_llm) -> dict:
    """Resume a paused run after a human has made a decision."""

    with _tracer.start_as_current_span("agent_resume") as run_span:
        run_span.set_attribute("thread_id", thread_id)
        run_span.set_attribute("decision_outcome", decision.get("outcome", "unknown"))

        compiled_graph = build_graph(registry, queue, llm_call=llm_call)
        config = {"configurable": {"thread_id": thread_id}}

        result = compiled_graph.invoke(Command(resume=decision), config=config)

        if "__interrupt__" in result:
            interrupt_data = result["__interrupt__"][0].value
            return {"status": "awaiting_approval", "approval_request_id": interrupt_data["approval_request_id"]}

        return {"status": "completed", "state": AgentState(**result)}