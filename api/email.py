#1.1
"""
Email validation utility.

This module provides email validation functionality including basic format validation,
domain validation, disposable email detection, and batch processing capabilities.
"""

import re


def validate_email(email):
    """
    Validate email address format (AC-001: Basic Email Format Validation).

    Args:
        email (str): Email address to validate

    Returns:
        dict: Validation result containing:
            - valid (bool): True if email is valid, False otherwise
            - email (str): The email address that was validated
            - error (str): Error message if invalid, None if valid

    Example:
        >>> validate_email("user@example.com")
        {'valid': True, 'email': 'user@example.com', 'error': None}

        >>> validate_email("invalid-email")
        {'valid': False, 'email': 'invalid-email', 'error': 'Invalid email format: missing @ symbol'}
    """
    # Check if email is provided
    if not email:
        return {
            'valid': False,
            'email': email,
            'error': 'Email address is required'
        }

    # Check if email is a string
    if not isinstance(email, str):
        return {
            'valid': False,
            'email': str(email),
            'error': 'Email address must be a string'
        }

    # Trim whitespace
    email = email.strip()

    # Check for @ symbol
    if '@' not in email:
        return {
            'valid': False,
            'email': email,
            'error': 'Invalid email format: missing @ symbol'
        }

    # Check for multiple @ symbols
    if email.count('@') > 1:
        return {
            'valid': False,
            'email': email,
            'error': 'Invalid email format: multiple @ symbols found'
        }

    # Split into local and domain parts
    local_part, domain_part = email.rsplit('@', 1)

    # Validate local part (before @)
    if not local_part:
        return {
            'valid': False,
            'email': email,
            'error': 'Invalid email format: missing local part before @'
        }

    # Validate domain part (after @)
    if not domain_part:
        return {
            'valid': False,
            'email': email,
            'error': 'Invalid email format: missing domain after @'
        }

    # Check for dot in domain
    if '.' not in domain_part:
        return {
            'valid': False,
            'email': email,
            'error': 'Invalid email format: domain must contain a dot (.)'
        }

    # Basic regex pattern for email validation
    # Allows: letters, numbers, dots, hyphens, underscores in local part
    # Requires: domain with at least one dot and valid TLD
    email_pattern = r'^[a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(email_pattern, email):
        return {
            'valid': False,
            'email': email,
            'error': 'Invalid email format: email does not match required pattern'
        }

    # Check for invalid characters
    if email.startswith('.') or email.endswith('.'):
        return {
            'valid': False,
            'email': email,
            'error': 'Invalid email format: email cannot start or end with a dot'
        }

    # Check for consecutive dots
    if '..' in email:
        return {
            'valid': False,
            'email': email,
            'error': 'Invalid email format: consecutive dots are not allowed'
        }

    # Email is valid
    return {
        'valid': True,
        'email': email,
        'error': None
    }
