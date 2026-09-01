import json
from typing import Callable
from app.agent.llm import call_llm
from app.agent.state import AgentState
from app.tools.registry import ToolRegistry

def _build_tool_catalog_text(registry: ToolRegistry) -> str:
    """Describe the available tools as plain text, for the prompt."""
    lines = []
    for tool in registry.list_tools():
        lines.append(f"{tool.name}: {tool.description}")
    return "\n".join(lines)

def _build_prompt(user_message: str, registry: ToolRegistry) -> str:
    tool_catalog = _build_tool_catalog_text(registry)

    return f"""You are deciding which tool (if any) should handle a user's request.

Available tools:
{tool_catalog}

User request: "{user_message}"

Respond with ONLY valid JSON in this exact shape, nothing else:
{{"tool": "<tool_name or null>", "input": {{<input fields for that tool>}}, "reasoning": "<short explanation>"}}

If no tool is needed (e.g. it's just a question you can answer directly), set "tool" to null and "input" to {{}}.
"""

def plan(state: AgentState, registry: ToolRegistry, llm_call: Callable[[str], str] = call_llm) -> AgentState:
    """Decide what should happen next for this request, and update the state."""

    prompt = _build_prompt(state.user_message, registry)
    raw_response = llm_call(prompt)

    try:
        decision = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Plan node got a non-JSON response from the LLM: {raw_response!r}") from exc

    tool_name = decision.get("tool")
    tool_input = decision.get("input", {})
    reasoning = decision.get("reasoning", "")

    if tool_name is not None:
        known_tool_names = {tool.name for tool in registry.list_tools()}
        if tool_name not in known_tool_names:
            raise ValueError(f"Plan node chose an unknown tool: '{tool_name}'")

    return state.model_copy(
        update={
            "plan": reasoning,
            "selected_tool": tool_name,
            "tool_input": tool_input,
        }
    )