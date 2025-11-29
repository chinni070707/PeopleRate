"""
Security utilities for PeopleRate
Input sanitization, validation, and security helpers
"""

import re
import bleach
from typing import Optional
import secrets
import string

# Allowed HTML tags for rich text (none for now - plain text only)
ALLOWED_TAGS = []
ALLOWED_ATTRIBUTES = {}

# Password complexity requirements
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGIT = True
PASSWORD_REQUIRE_SPECIAL = False


def sanitize_html(text: str) -> str:
    """
    Sanitize HTML input to prevent XSS attacks
    Strips all HTML tags and returns plain text
    """
    if not text:
        return ""
    
    # Remove all HTML tags and attributes
    cleaned = bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
    
    return cleaned.strip()


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize user input text
    - Remove HTML
    - Trim whitespace
    - Limit length
    """
    if not text:
        return ""
    
    # Sanitize HTML
    cleaned = sanitize_html(text)
    
    # Remove extra whitespace
    cleaned = ' '.join(cleaned.split())
    
    # Limit length if specified
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    return cleaned


def validate_email_format(email: str) -> bool:
    """
    Validate email format using regex
    More restrictive than email-validator for security
    """
    if not email:
        return False
    
    # Email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Basic checks
    if len(email) > 320:  # Max email length per RFC
        return False
    
    if not re.match(pattern, email):
        return False
    
    # Check for suspicious patterns
    suspicious_patterns = [
        r'\.\.', # Double dots
        r'^\.', # Starts with dot
        r'\.$', # Ends with dot
        r'@.*@', # Multiple @ symbols
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, email):
            return False
    
    return True


def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate username format and security
    Returns: (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"
    
    # Length check
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 30:
        return False, "Username must be at most 30 characters"
    
    # Character check: alphanumeric, underscore, hyphen only
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    
    # Must start with letter or number
    if not re.match(r'^[a-zA-Z0-9]', username):
        return False, "Username must start with a letter or number"
    
    # Blacklist check (reserved words)
    blacklist = [
        'admin', 'administrator', 'root', 'system', 'moderator', 'mod',
        'staff', 'support', 'help', 'info', 'contact', 'about', 'terms',
        'privacy', 'legal', 'api', 'auth', 'login', 'logout', 'register',
        'signup', 'signin', 'null', 'undefined', 'none', 'test', 'demo'
    ]
    
    if username.lower() in blacklist:
        return False, "This username is reserved"
    
    return True, ""


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    # Length check
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters"
    
    if len(password) > 128:
        return False, "Password must be at most 128 characters"
    
    # Complexity checks
    checks = []
    
    if PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
        checks.append("one uppercase letter")
    
    if PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
        checks.append("one lowercase letter")
    
    if PASSWORD_REQUIRE_DIGIT and not re.search(r'\d', password):
        checks.append("one digit")
    
    if PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        checks.append("one special character")
    
    if checks:
        return False, f"Password must contain {', '.join(checks)}"
    
    # Check for common weak passwords
    common_passwords = [
        'password', '12345678', 'password123', 'qwerty', 'abc123',
        'letmein', 'welcome', 'monkey', '1234567890', 'password1'
    ]
    
    if password.lower() in common_passwords:
        return False, "This password is too common"
    
    return True, ""


def sanitize_url(url: str) -> Optional[str]:
    """
    Sanitize and validate URL input
    Returns sanitized URL or None if invalid
    """
    if not url:
        return None
    
    url = url.strip()
    
    # Must start with http:// or https://
    if not re.match(r'^https?://', url, re.IGNORECASE):
        # Prepend https:// if missing
        url = f"https://{url}"
    
    # Basic URL validation
    url_pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    if not re.match(url_pattern, url):
        return None
    
    # Check for suspicious patterns
    suspicious_patterns = [
        r'javascript:', # XSS attempts
        r'data:', # Data URLs
        r'file:', # File URLs
        r'<script', # Script tags
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return None
    
    # Limit length
    if len(url) > 2048:
        return None
    
    return url


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def validate_social_media_url(platform: str, url: str) -> bool:
    """
    Validate social media URL format for specific platforms
    """
    if not url:
        return True  # Empty is allowed (optional fields)
    
    url = url.strip()
    
    # Platform-specific validation
    patterns = {
        'linkedin': r'^https?://(www\.)?linkedin\.com/in/[\w-]+/?$',
        'instagram': r'^https?://(www\.)?instagram\.com/[\w.]+/?$',
        'facebook': r'^https?://(www\.)?facebook\.com/[\w.]+/?$',
        'twitter': r'^https?://(www\.)?(twitter|x)\.com/[\w]+/?$',
        'github': r'^https?://(www\.)?github\.com/[\w-]+/?$',
    }
    
    if platform.lower() not in patterns:
        # Generic URL validation
        return sanitize_url(url) is not None
    
    pattern = patterns[platform.lower()]
    return re.match(pattern, url, re.IGNORECASE) is not None


def is_suspicious_ip(ip_address: str) -> bool:
    """
    Check if IP address shows suspicious patterns
    (Placeholder for future IP reputation checks)
    """
    if not ip_address:
        return False
    
    # Local/private IPs are fine
    private_ranges = [
        r'^127\.',  # Localhost
        r'^10\.',   # Private network
        r'^192\.168\.',  # Private network
        r'^172\.(1[6-9]|2[0-9]|3[01])\.',  # Private network
    ]
    
    for pattern in private_ranges:
        if re.match(pattern, ip_address):
            return False
    
    # TODO: Add IP reputation check with external service
    # For now, all non-private IPs are considered ok
    return False


def sanitize_search_query(query: str) -> str:
    """
    Sanitize search query to prevent injection attacks
    """
    if not query:
        return ""
    
    # Remove special regex characters that could cause issues
    query = re.sub(r'[\\$^*+?{}\[\]().|]', '', query)
    
    # Remove HTML
    query = sanitize_html(query)
    
    # Limit length
    if len(query) > 200:
        query = query[:200]
    
    # Trim whitespace
    query = ' '.join(query.split())
    
    return query


# Export all functions
__all__ = [
    'sanitize_html',
    'sanitize_input',
    'validate_email_format',
    'validate_username',
    'validate_password_strength',
    'sanitize_url',
    'generate_secure_token',
    'validate_social_media_url',
    'is_suspicious_ip',
    'sanitize_search_query',
]
