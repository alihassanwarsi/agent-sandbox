import pytest
from pydantic import ValidationError

from app.agent.role import AgentCapability, AgentRole, WORKSPACE_ASSISTANT_ROLE


def test_workspace_assistant_has_expected_capabilities():
    expected = {
        AgentCapability.ANSWER_QUESTIONS,
        AgentCapability.INSPECT_FILES,
        AgentCapability.SUMMARIZE_DATA,
        AgentCapability.CALL_SAFE_APIS,
        AgentCapability.PREPARE_ACTIONS_FOR_APPROVAL,
    }
    assert set(WORKSPACE_ASSISTANT_ROLE.capabilities) == expected


def test_has_capability_returns_true_when_allowed():
    assert WORKSPACE_ASSISTANT_ROLE.has_capability(
        AgentCapability.INSPECT_FILES
    ) is True


def test_has_capability_returns_false_when_not_allowed():
    small_role = AgentRole(
        name="small_role",
        description="Test role with a single capability.",
        capabilities=(AgentCapability.ANSWER_QUESTIONS,),
        core_principle="Test rule.",
    )
    assert small_role.has_capability(AgentCapability.CALL_SAFE_APIS) is False


def test_role_cannot_be_changed_after_creation():
    with pytest.raises(ValidationError):
        WORKSPACE_ASSISTANT_ROLE.name = "changed_name"


def test_role_requires_at_least_one_capability():
    with pytest.raises(ValidationError):
        AgentRole(
            name="empty_role",
            description="No capabilities.",
            capabilities=(),
            core_principle="Test rule.",
        )