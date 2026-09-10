from app.agent.state import AgentState

def approval_wait(state: AgentState) -> AgentState:
    """Mark the request as awaiting approval and return it."""

    return state.model_copy(
        update={
            "awaiting_approval": True,
            "final_response":(
                f"This action ('{state.selected_tool}') is high-risk and requires "
                f"human approval before it can run. It has been queued for review."
            )
        }
    )
