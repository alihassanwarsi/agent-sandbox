from app.agent.state import AgentState
from app.permissions.roles import UserRole

def intake(user_message: str, role: UserRole) -> AgentState:
    """Build the initial AgentState from a raw incoming request."""

    if not user_message.strip():
        raise ValueError("user_message cannot be empty.")
    
    return AgentState(user_message=user_message, role=role)