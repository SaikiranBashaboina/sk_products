"""Reusable validation utilities."""

import re
from typing import Optional


def validate_email(email: str) -> str:
    """Validate and normalize email address."""
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        raise ValueError("Invalid email format")
    return email.lower()


def validate_password(password: str, require_letter: bool = True, require_number: bool = True) -> str:
    """Validate password strength with configurable requirements.

    Rules:
    - Minimum 8 characters (increased for production security)
    - At least one letter (optional, configurable)
    - At least one number (optional, configurable)
    - At least one special character (recommended)

    Returns the validated password.
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")

    if require_letter and not re.search(r"[A-Za-z]", password):
        raise ValueError("Password must contain at least one letter")

    if require_number and not re.search(r"\d", password):
        raise ValueError("Password must contain at least one number")

    # Recommend special characters for stronger security
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        raise ValueError("Password must contain at least one special character (!@#$%^&*...)")

    return password
