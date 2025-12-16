"""Phone number formatter and validator utility."""

import re


def validate_phone_number(phone_number: str) -> bool:
    """
    Validate that a phone number contains more than 5 digits.

    Args:
        phone_number: The phone number string to validate

    Returns:
        bool: True if phone number has more than 5 digits, False otherwise
    """
    if not phone_number:
        return False

    # Extract only digits from the phone number
    digits = re.sub(r'\D', '', phone_number)

    # Check if there are more than 5 digits
    return len(digits) > 5
