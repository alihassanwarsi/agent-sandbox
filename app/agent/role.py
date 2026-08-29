from enum import Enum
from pydantic import BaseModel, ConfigDict, Field

class AgentCapability(str, Enum):
    """A discrete thing the agent is scoped to be able to do."""

    ANSWER_QUESTIONS = "answer_questions"
    INSPECT_FILES = "inspect_files"
    SUMMARIZE_DATA = "summarize_data"
    CALL_SAFE_APIS = "call_safe_apis"
    PREPARE_ACTIONS_FOR_APPROVAL = "prepare_actions_for_approval"

class AgentRole(BaseModel):
    """Formal definition of an agent's identity and scope."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., min_length=1, description="Name of the role")
    description: str = Field(..., min_length=1, description="Summary of the Agent's purpose")
    capabilities: tuple[AgentCapability, ...] = Field(..., min_length=1, description="The set of things this agent is scoped to do.")
    core_principle: str = Field(..., min_length=1, description="The governing safety principle for this agent's behavior.")

    def has_capability(self, capability: AgentCapability) -> bool:
        """Return True if this role is scoped to perform the given capability."""
        return capability in self.capabilities


WORKSPACE_ASSISTANT_ROLE = AgentRole(
    name = "workspace_assistant",
    description= "An assistant that can answer questions, inspect files, summarize data, call safe APIs, and prepare actions for human approval.",
    capabilities=(
        AgentCapability.ANSWER_QUESTIONS,
        AgentCapability.INSPECT_FILES,
        AgentCapability.SUMMARIZE_DATA,
        AgentCapability.CALL_SAFE_APIS,
        AgentCapability.PREPARE_ACTIONS_FOR_APPROVAL
    ),
    core_principle= "The model proposes, the system disposes. Deterministic permission checks decide what can actually be executed."
)