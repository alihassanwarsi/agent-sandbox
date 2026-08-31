from app.permissions.risk import RiskLevel, TOOL_RISK_LEVELS
from app.permissions.roles import UserRole

MAX_RISK_BY_ROLE: dict[UserRole, RiskLevel] = {
    UserRole.VIEWER: RiskLevel.LOW,
    UserRole.ANALYST: RiskLevel.MEDIUM,
    UserRole.OPERATOR: RiskLevel.HIGH,
    UserRole.ADMIN: RiskLevel.HIGH,
}

class PermissionDenied(Exception):
    """Raised when a role is not allowed to use a given tool."""

def check_permission(role: UserRole, tool_name: str) -> None:


    if tool_name not in TOOL_RISK_LEVELS:
        raise ValueError(f"Unknown tool '{tool_name}': no risk level is registered for it.")

    tool_risk = TOOL_RISK_LEVELS[tool_name]
    allowed_risk = MAX_RISK_BY_ROLE[role]

    if tool_risk > allowed_risk:
        raise PermissionDenied(
            f"Role '{role.name}' is not permitted to use tool '{tool_name}'"
            f"(tool risk: {tool_risk.name}, role's max allowed risk: {allowed_risk.name})."
        )