from app.permissions.roles import UserRole

def test_roles_are_ordered_correctly():
    assert UserRole.VIEWER < UserRole.ANALYST
    assert UserRole.ANALYST < UserRole.OPERATOR
    assert UserRole.OPERATOR < UserRole.ADMIN

def test_admin_has_highest_access():
    assert UserRole.ADMIN > UserRole.VIEWER
    assert UserRole.ADMIN >= UserRole.OPERATOR