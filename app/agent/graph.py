from langgraph.graph import START, END, StateGraph
from app.agent.nodes.intake import intake
from app.agent.nodes.plan import plan
from app.agent.nodes.permission_check import permission_check
from app.agent.nodes.execution import execution
from app.agent.nodes.reflection import reflection
from app.agent.state import AgentState
from app.permissions.roles import UserRole
from app.tools.registry import ToolRegistry

def build_graph(registry: ToolRegistry):
    """Build and compile the LangGraph pipeline, bound to the given tool registry."""

    def plan_node(state: AgentState) -> dict:
        return plan(state, registry).model_dump()

    def permission_check_node(state: AgentState) -> dict:
        return permission_check(state).model_dump()

    def execution_node(state: AgentState) -> dict:
        return execution(state, registry).model_dump()

    def reflection_node(state: AgentState) -> dict:
        return reflection(state).model_dump()
    
    graph = StateGraph(AgentState)

    graph.add_node("plan", plan_node)
    graph.add_node("permission_check", permission_check_node)
    graph.add_node("execution", execution_node)
    graph.add_node("reflection", reflection_node)

    graph.add_edge(START, "plan")
    graph.add_edge("plan", "permission_check")
    graph.add_edge("permission_check", "execution")
    graph.add_edge("execution", "reflection")
    graph.add_edge("reflection", END)

    return graph.compile()

def run_agent(user_message: str, role: UserRole, registry: ToolRegistry) -> AgentState:
    """Run the full pipeline for one request, returning the final AgentState."""

    initial_state = intake(user_message, role)
    compiled_graph = build_graph(registry)

    result = compiled_graph.invoke(initial_state)

    return AgentState(**result)