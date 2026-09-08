import pytest
from app.permissions.checks import check_permission, check_confirmation, PermissionDenied, ConfirmationRequired
from app.permissions.roles import UserRole


def test_viewer_can_use_low_risk_tool():
    check_permission(UserRole.VIEWER, "calculator")  # should not raise

def test_viewer_cannot_use_high_risk_tool():
    with pytest.raises(PermissionDenied):
        check_permission(UserRole.VIEWER, "create_ticket")

def test_viewer_cannot_use_medium_risk_tool():
    with pytest.raises(PermissionDenied):
        check_permission(UserRole.VIEWER, "file_reader")

def test_analyst_can_use_medium_risk_tool():
    check_permission(UserRole.ANALYST, "csv_reader")  

def test_analyst_cannot_use_high_risk_tool():
    with pytest.raises(PermissionDenied):
        check_permission(UserRole.ANALYST, "create_ticket")

def test_operator_can_use_high_risk_tool():
    check_permission(UserRole.OPERATOR, "create_ticket")  

def test_admin_can_use_any_tool():
    check_permission(UserRole.ADMIN, "create_ticket")  
    check_permission(UserRole.ADMIN, "calculator")  

def test_unknown_tool_raises_value_error():
    with pytest.raises(ValueError):
        check_permission(UserRole.ADMIN, "not_a_real_tool")

def test_medium_risk_tool_without_confirmation_raises_error():
    with pytest.raises(ConfirmationRequired):
        check_confirmation("file_reader", confirmed=False)

def test_medium_risk_tool_with_confirmation_passes():
    check_confirmation("file_reader", confirmed=True)

def test_low_risk_tool_never_needs_confirmation():
    check_confirmation("calculator", confirmed=False)

def test_high_risk_tool_is_not_handled_by_confirmation():
    check_confirmation("create_ticket", confirmed=False) 