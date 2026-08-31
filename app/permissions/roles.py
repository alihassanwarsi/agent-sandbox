from enum import IntEnum

class UserRole(IntEnum):
    """Defines user roles by access level."""

    VIEWER = 1
    ANALYST = 2
    OPERATOR = 3
    ADMIN = 4