import hashlib
import secrets
from datetime import datetime, timedelta

class PasswordResetManager:
    """Manages password reset tokens and operations"""
    
    def __init__(self):
        self.reset_tokens = {}
    
    def generate_reset_token(self, email):
        """
        Generate a secure reset token for the given email
        
        Args:
            email: User's email address
            
        Returns:
            dict: Token information with expiry
        """
        if not email or '@' not in email:
            raise ValueError("Invalid email address")
        
        # Generate secure random token
        token = secrets.token_urlsafe(32)
        
        # Set expiry to 1 hour from now
        expiry = datetime.now() + timedelta(hours=1)
        
        # Store token with email and expiry
        self.reset_tokens[token] = {
            'email': email,
            'expiry': expiry,
            'used': False
        }
        
        return {
            'token': token,
            'expiry': expiry.isoformat(),
            'reset_url': f"https://example.com/reset?token={token}"
        }
    
    def validate_token(self, token):
        """
        Validate if a reset token is valid and not expired
        
        Args:
            token: Reset token to validate
            
        Returns:
            dict: Validation result with email if valid
        """
        if not token:
            return {'valid': False, 'error': 'Token is required'}
        
        if token not in self.reset_tokens:
            return {'valid': False, 'error': 'Invalid token'}
        
        token_data = self.reset_tokens[token]
        
        # Check if already used
        if token_data['used']:
            return {'valid': False, 'error': 'Token already used'}
        
        # Check if expired
        if datetime.now() > token_data['expiry']:
            return {'valid': False, 'error': 'Token has expired'}
        
        return {
            'valid': True,
            'email': token_data['email']
        }
    
    def reset_password(self, token, new_password):
        """
        Reset password using a valid token
        
        Args:
            token: Valid reset token
            new_password: New password to set
            
        Returns:
            dict: Result of password reset operation
        """
        # Validate token first
        validation = self.validate_token(token)
        if not validation['valid']:
            return {
                'success': False,
                'error': validation['error']
            }
        
        # Validate new password
        if not new_password or len(new_password) < 8:
            return {
                'success': False,
                'error': 'Password must be at least 8 characters'
            }
        
        # Mark token as used
        self.reset_tokens[token]['used'] = True
        
        # Hash the password (simplified for demo)
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        return {
            'success': True,
            'email': validation['email'],
            'message': 'Password reset successfully'
        }
    
    def cleanup_expired_tokens(self):
        """Remove expired tokens from storage"""
        current_time = datetime.now()
        expired = [
            token for token, data in self.reset_tokens.items()
            if current_time > data['expiry']
        ]
        
        for token in expired:
            del self.reset_tokens[token]

        return {'removed': len(expired)}