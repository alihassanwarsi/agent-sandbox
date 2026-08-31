from enum import IntEnum

class RiskLevel(IntEnum):
    """Defines tool risk levels."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3

TOOL_RISK_LEVELS: dict[str, RiskLevel] = {
    "calculator": RiskLevel.LOW,
    "file_reader": RiskLevel.MEDIUM,
    "web_search": RiskLevel.LOW,
    "csv_reader": RiskLevel.MEDIUM,
    "create_ticket": RiskLevel.HIGH,
}