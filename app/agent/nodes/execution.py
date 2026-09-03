from app.agent.state import AgentState
from app.tools.registry import ToolRegistry

def execution(state: AgentState, registry: ToolRegistry) -> AgentState:
    """Run the selected tool (if permitted) and store its result."""

    if state.selected_tool is None:
        return state

    if state.permission_error is not None:
        return state

    tool = registry.get(state.selected_tool)

    input_data = tool.input_schema(**(state.tool_input or {}))

    result = registry.run(state.selected_tool, state.role, input_data)

    return state.model_copy(update={"tool_result": result})