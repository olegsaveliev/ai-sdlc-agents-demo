"""
Advanced email validation utility with domain validation.

This module provides advanced email validation functionality including domain
existence verification and reachability checks (AC-002: Domain Validation).
"""

import socket
import dns.resolver
from api.email import validate_email


def validate_domain(domain):
    """
    Validate domain existence and reachability (AC-002: Domain Validation).

    Checks if a domain exists by verifying DNS records (MX or A records).

    Args:
        domain (str): Domain name to validate

    Returns:
        dict: Validation result containing:
            - valid (bool): True if domain exists and is reachable, False otherwise
            - domain (str): The domain that was validated
            - error (str): Error message if invalid, None if valid
            - mx_records (list): List of MX records if found, empty list otherwise
            - has_mx (bool): True if MX records exist
            - has_a (bool): True if A records exist

    Example:
        >>> validate_domain("gmail.com")
        {'valid': True, 'domain': 'gmail.com', 'error': None, 'mx_records': [...], 'has_mx': True, 'has_a': True}

        >>> validate_domain("nonexistentdomain123456.com")
        {'valid': False, 'domain': 'nonexistentdomain123456.com', 'error': 'Domain does not exist', ...}
    """
    if not domain:
        return {
            'valid': False,
            'domain': domain,
            'error': 'Domain is required',
            'mx_records': [],
            'has_mx': False,
            'has_a': False
        }

    if not isinstance(domain, str):
        return {
            'valid': False,
            'domain': str(domain),
            'error': 'Domain must be a string',
            'mx_records': [],
            'has_mx': False,
            'has_a': False
        }

    domain = domain.strip().lower()

    # Initialize result
    result = {
        'valid': False,
        'domain': domain,
        'error': None,
        'mx_records': [],
        'has_mx': False,
        'has_a': False
    }

    # Check for MX records (mail exchange records)
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        result['mx_records'] = [str(record.exchange) for record in mx_records]
        result['has_mx'] = True
        result['valid'] = True
        return result
    except dns.resolver.NXDOMAIN:
        result['error'] = 'Domain does not exist'
        return result
    except dns.resolver.NoAnswer:
        # No MX records, but domain might still exist - check A records
        pass
    except dns.resolver.Timeout:
        result['error'] = 'Domain lookup timed out'
        return result
    except Exception as e:
        result['error'] = f'DNS lookup error: {str(e)}'
        return result

    # If no MX records, check for A records (domain exists but may not accept email)
    try:
        a_records = dns.resolver.resolve(domain, 'A')
        result['has_a'] = True
        result['valid'] = True
        result['error'] = 'Domain exists but has no MX records (may not accept email)'
        return result
    except dns.resolver.NXDOMAIN:
        result['error'] = 'Domain does not exist'
        return result
    except dns.resolver.NoAnswer:
        result['error'] = 'Domain exists but has no DNS records'
        return result
    except dns.resolver.Timeout:
        result['error'] = 'Domain lookup timed out'
        return result
    except Exception as e:
        result['error'] = f'DNS lookup error: {str(e)}'
        return result


def validate_email_with_domain(email, check_domain=True):
    """
    Validate email with optional domain checking (AC-002: Domain Validation).

    When domain checking is enabled, verifies domain existence and reachability,
    distinguishing between valid domains (e.g., gmail.com) and nonexistent ones.

    Args:
        email (str): Email address to validate
        check_domain (bool): If True, perform domain validation. Default: True

    Returns:
        dict: Validation result containing:
            - valid (bool): True if email is valid (format and domain if checked), False otherwise
            - email (str): The email address that was validated
            - error (str): Error message if invalid, None if valid
            - format_valid (bool): True if email format is valid
            - domain_valid (bool): True if domain is valid (only if check_domain=True)
            - domain_info (dict): Domain validation details (only if check_domain=True)

    Example:
        >>> validate_email_with_domain("user@gmail.com")
        {'valid': True, 'email': 'user@gmail.com', 'error': None, 'format_valid': True, 'domain_valid': True, ...}

        >>> validate_email_with_domain("user@nonexistentdomain123456.com")
        {'valid': False, 'email': 'user@...', 'error': 'Domain does not exist', 'format_valid': True, 'domain_valid': False, ...}

        >>> validate_email_with_domain("invalid-email")
        {'valid': False, 'email': 'invalid-email', 'error': 'Invalid email format: missing @ symbol', 'format_valid': False, ...}
    """
    # First, validate email format
    format_result = validate_email(email)

    result = {
        'valid': format_result['valid'],
        'email': format_result['email'],
        'error': format_result['error'],
        'format_valid': format_result['valid'],
        'domain_valid': None,
        'domain_info': None
    }

    # If format is invalid or domain checking is disabled, return early
    if not format_result['valid'] or not check_domain:
        return result

    # Extract domain from email
    domain = email.split('@')[1] if '@' in email else ''

    # Validate domain
    domain_result = validate_domain(domain)
    result['domain_valid'] = domain_result['valid']
    result['domain_info'] = domain_result

    # Update overall validity and error message
    if not domain_result['valid']:
        result['valid'] = False
        result['error'] = domain_result['error']
    elif domain_result['error']:
        # Domain exists but has issues (e.g., no MX records)
        result['error'] = domain_result['error']

    return result
