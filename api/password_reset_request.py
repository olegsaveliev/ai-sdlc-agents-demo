#1
"""
Password Reset Request API - US001 Implementation
Implements the password reset request flow for issue #29
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Optional
from api.password_reset import PasswordResetManager


class RateLimiter:
    """Rate limiting for password reset requests"""

    def __init__(self, max_requests: int = 3, window_minutes: int = 15):
        self.max_requests = max_requests
        self.window_minutes = window_minutes
        self.requests = {}  # email -> list of timestamps

    def is_allowed(self, email: str) -> bool:
        """Check if request is allowed based on rate limits"""
        now = datetime.now()

        # Initialize if first request
        if email not in self.requests:
            self.requests[email] = []

        # Clean up old requests outside the window
        window_start = now - timedelta(minutes=self.window_minutes)
        self.requests[email] = [
            ts for ts in self.requests[email]
            if ts > window_start
        ]

        # Check if under limit
        if len(self.requests[email]) >= self.max_requests:
            return False

        # Record this request
        self.requests[email].append(now)
        return True

    def get_retry_after(self, email: str) -> Optional[int]:
        """Get seconds until next request is allowed"""
        if email not in self.requests or not self.requests[email]:
            return None

        oldest_request = min(self.requests[email])
        retry_time = oldest_request + timedelta(minutes=self.window_minutes)
        seconds_left = (retry_time - datetime.now()).total_seconds()

        return max(0, int(seconds_left))


class EmailService:
    """Simple email service for sending password reset emails"""

    def send_reset_email(self, email: str, reset_token: str, reset_url: str) -> bool:
        """
        Send password reset email to user

        Args:
            email: Recipient email address
            reset_token: Unique reset token
            reset_url: URL for password reset

        Returns:
            bool: True if email sent successfully
        """
        # In a real implementation, this would use SMTP or email service provider
        # For now, we'll simulate email sending

        email_body = f"""
Dear User,

You recently requested to reset your password for your account.

Click the link below to reset your password:
{reset_url}

If you did not request this password reset, please ignore this email or contact support if you have concerns.

For security reasons:
- This link will expire in 1 hour
- Do not share this link with anyone
- We will never ask for your password via email

Best regards,
The Application Team
"""

        # Simulate email sending (in production, integrate with actual email service)
        print(f"[EMAIL] Sending to: {email}")
        print(f"[EMAIL] Reset URL: {reset_url}")
        print(f"[EMAIL] Body:\n{email_body}")

        return True


class PasswordResetRequestAPI:
    """API endpoint handler for password reset requests - US001"""

    def __init__(self):
        self.reset_manager = PasswordResetManager()
        self.rate_limiter = RateLimiter(max_requests=3, window_minutes=15)
        self.email_service = EmailService()
        # Simulated user database (in production, use actual database)
        self.registered_emails = set()

    def register_user(self, email: str):
        """Helper method to simulate user registration"""
        self.registered_emails.add(email.lower())

    def is_registered_email(self, email: str) -> bool:
        """Check if email is registered in the system"""
        return email.lower() in self.registered_emails

    def request_password_reset(self, email: str, ip_address: Optional[str] = None) -> Dict:
        """
        POST /api/auth/password-reset/request

        Initiate password reset process for a user

        Args:
            email: User's email address
            ip_address: IP address of requester (for audit logging)

        Returns:
            dict: Response with success status and message
        """
        # Validate email format
        if not email or '@' not in email:
            return {
                'success': False,
                'message': 'Invalid email format'
            }

        email = email.lower().strip()

        # Check rate limiting
        if not self.rate_limiter.is_allowed(email):
            retry_after = self.rate_limiter.get_retry_after(email)
            return {
                'success': False,
                'message': f'Too many reset requests. Please try again in {retry_after // 60} minutes.',
                'retry_after': retry_after
            }

        # Security measure: Always return same message whether email exists or not
        # This prevents email enumeration attacks
        generic_message = 'If the email exists in our system, you will receive reset instructions.'

        # Only proceed with token generation if email is registered
        if self.is_registered_email(email):
            try:
                # Generate reset token
                token_info = self.reset_manager.generate_reset_token(email)

                # Send email with reset link
                reset_url = token_info['reset_url']
                email_sent = self.email_service.send_reset_email(
                    email=email,
                    reset_token=token_info['token'],
                    reset_url=reset_url
                )

                if not email_sent:
                    # Log error but don't reveal to user
                    print(f"[ERROR] Failed to send email to {email}")

                # Log the request (in production, log to audit table)
                print(f"[AUDIT] Password reset requested for {email} from IP {ip_address}")

            except Exception as e:
                # Log error but don't reveal details to user
                print(f"[ERROR] Password reset request failed: {str(e)}")

        # Always return generic success message for security
        return {
            'success': True,
            'message': generic_message
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize API
    api = PasswordResetRequestAPI()

    # Register some test users
    api.register_user("user@example.com")
    api.register_user("admin@example.com")

    print("=== Test 1: Valid email (registered) ===")
    result = api.request_password_reset("user@example.com", ip_address="192.168.1.1")
    print(f"Result: {result}\n")

    print("=== Test 2: Valid email (not registered) ===")
    result = api.request_password_reset("unknown@example.com", ip_address="192.168.1.1")
    print(f"Result: {result}\n")

    print("=== Test 3: Invalid email format ===")
    result = api.request_password_reset("notanemail", ip_address="192.168.1.1")
    print(f"Result: {result}\n")

    print("=== Test 4: Rate limiting (4 requests to same email) ===")
    for i in range(4):
        result = api.request_password_reset("user@example.com", ip_address="192.168.1.1")
        print(f"Request {i+1}: {result}")
