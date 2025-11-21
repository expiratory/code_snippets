"""Password validation utilities."""

import re
from typing import Tuple


def validate_password_strength(password: str) -> Tuple[bool, list[str]]:
    """
    Validate password strength.

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")

    if not re.search(r"\d", password):
        errors.append("Password must contain at least one digit")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append(
            'Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)'
        )

    if re.search(r"(.)\1{3,}", password):
        errors.append("Password contains too many repeating characters")

    sequential_patterns = [
        "0123456789",
        "abcdefghijklmnopqrstuvwxyz",
        "qwertyuiop",
        "asdfghjkl",
        "zxcvbnm",
    ]
    password_lower = password.lower()
    for pattern in sequential_patterns:
        for i in range(len(pattern) - 3):
            if (
                pattern[i : i + 4] in password_lower
                or pattern[i : i + 4][::-1] in password_lower
            ):
                errors.append("Password contains sequential characters")
                break
        if "Password contains sequential characters" in errors:
            break

    return (len(errors) == 0, errors)
