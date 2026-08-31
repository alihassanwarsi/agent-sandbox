from app.permissions.risk import RiskLevel, TOOL_RISK_LEVELS

def test_every_starter_tool_has_a_risk_level():
    expected_tools = {"calculator", "file_reader", "web_search", "csv_reader", "create_ticket"}
    assert set(TOOL_RISK_LEVELS.keys()) == expected_tools

def test_create_ticket_is_high_risk():
    assert TOOL_RISK_LEVELS["create_ticket"] == RiskLevel.HIGH

def test_calculator_is_low_risk():
    assert TOOL_RISK_LEVELS["calculator"] == RiskLevel.LOW

def test_risk_levels_are_ordered_correctly():
    assert RiskLevel.LOW < RiskLevel.MEDIUM < RiskLevel.HIGH