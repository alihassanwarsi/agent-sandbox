from typing import Callable
from app.agent.llm import call_llm
from app.agent.state import AgentState

def _build_result_prompt(user_message: str, tool_result: object) -> str:
    return f"""The user asked: "{user_message}"

A tool was run and produced this result: {tool_result}

Write a short, clear, natural language response to the user explaining this result. Do not mention that a "tool" was used, just answer naturally.
"""

def _build_direct_answer_prompt(user_message: str) -> str:
    return f"""The user asked: "{user_message}"

No tool is needed for this. Write a short, clear, natural-language response answering the user directly.
"""

def reflection(state: AgentState, llm_call: Callable[[str], str] = call_llm) -> AgentState:
    """Decide the final response to show the user, and update state."""

    if state.permission_error is not None:
        denial_message = (
            "I'm not able to complete that request: "
            f"{state.permission_error}"
        )

        return state.model_copy(update={"final_response": denial_message})

    if state.tool_result is not None:
        prompt = _build_result_prompt(state.user_message, state.tool_result)
        response_text = llm_call(prompt)
        return state.model_copy(update={"final_response": response_text})

    prompt = _build_direct_answer_prompt(state.user_message)
    response_text = llm_call(prompt)
    return state.model_copy(update={"final_response": response_text})