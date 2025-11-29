"""
Email Verification Service for PeopleRate
MVP implementation: File-based mock email system
Production: Replace with SendGrid/AWS SES
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
import json
from pathlib import Path

# Email verification storage (file-based for MVP)
VERIFICATION_DIR = Path("verification_emails")
VERIFICATION_DIR.mkdir(exist_ok=True)

VERIFICATION_TOKENS: Dict[str, Dict] = {}

def generate_verification_token(email: str, user_id: str) -> str:
    """
    Generate a verification token for email
    
    Args:
        email: User's email address
        user_id: User's ID
        
    Returns:
        Verification token string
    """
    token = secrets.token_urlsafe(32)
    
    VERIFICATION_TOKENS[token] = {
        "email": email,
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
        "verified": False
    }
    
    # Save to file for persistence
    _save_tokens()
    
    return token


def verify_token(token: str) -> Optional[Dict]:
    """
    Verify an email verification token
    
    Args:
        token: Verification token
        
    Returns:
        Token data if valid, None otherwise
    """
    _load_tokens()
    
    if token not in VERIFICATION_TOKENS:
        return None
    
    token_data = VERIFICATION_TOKENS[token]
    
    # Check if expired
    expires_at = datetime.fromisoformat(token_data["expires_at"])
    if datetime.utcnow() > expires_at:
        return None
    
    # Check if already verified
    if token_data["verified"]:
        return None
    
    # Mark as verified
    token_data["verified"] = True
    token_data["verified_at"] = datetime.utcnow().isoformat()
    _save_tokens()
    
    return token_data


def send_verification_email(email: str, user_id: str, username: str, base_url: str) -> str:
    """
    Send verification email (MVP: save to file, Production: send via SendGrid)
    
    Args:
        email: User's email address
        user_id: User's ID
        username: User's username
        base_url: Base URL for verification link
        
    Returns:
        Verification token
    """
    token = generate_verification_token(email, user_id)
    verification_link = f"{base_url}/verify-email?token={token}"
    
    # MVP: Save email to file
    email_content = f"""
    ================================
    PeopleRate Email Verification
    ================================
    
    Hi {username},
    
    Thanks for signing up for PeopleRate!
    
    Please verify your email address by clicking the link below:
    
    {verification_link}
    
    This link will expire in 24 hours.
    
    If you didn't create an account, you can safely ignore this email.
    
    Best regards,
    The PeopleRate Team
    
    ================================
    Email: {email}
    Token: {token}
    Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
    ================================
    """
    
    # Save to file (MVP implementation)
    filename = VERIFICATION_DIR / f"verify_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w") as f:
        f.write(email_content)
    
    print(f"📧 Verification email saved to: {filename}")
    print(f"🔗 Verification link: {verification_link}")
    
    return token


def send_password_reset_email(email: str, user_id: str, username: str, base_url: str) -> str:
    """
    Send password reset email (MVP: save to file)
    
    Args:
        email: User's email address
        user_id: User's ID
        username: User's username
        base_url: Base URL for reset link
        
    Returns:
        Reset token
    """
    token = secrets.token_urlsafe(32)
    reset_link = f"{base_url}/reset-password?token={token}"
    
    # Store reset token
    VERIFICATION_TOKENS[token] = {
        "email": email,
        "user_id": user_id,
        "type": "password_reset",
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        "used": False
    }
    _save_tokens()
    
    # MVP: Save email to file
    email_content = f"""
    ================================
    PeopleRate Password Reset
    ================================
    
    Hi {username},
    
    You requested to reset your password on PeopleRate.
    
    Click the link below to reset your password:
    
    {reset_link}
    
    This link will expire in 1 hour.
    
    If you didn't request this, you can safely ignore this email.
    
    Best regards,
    The PeopleRate Team
    
    ================================
    Email: {email}
    Token: {token}
    Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
    ================================
    """
    
    filename = VERIFICATION_DIR / f"reset_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w") as f:
        f.write(email_content)
    
    print(f"📧 Password reset email saved to: {filename}")
    print(f"🔗 Reset link: {reset_link}")
    
    return token


def _save_tokens():
    """Save tokens to file for persistence"""
    tokens_file = VERIFICATION_DIR / "tokens.json"
    with open(tokens_file, "w") as f:
        json.dump(VERIFICATION_TOKENS, f, indent=2)


def _load_tokens():
    """Load tokens from file"""
    global VERIFICATION_TOKENS
    tokens_file = VERIFICATION_DIR / "tokens.json"
    
    if tokens_file.exists():
        with open(tokens_file, "r") as f:
            VERIFICATION_TOKENS = json.load(f)


# Initialize by loading existing tokens
_load_tokens()


# TODO: Production implementation with SendGrid
"""
Production SendGrid implementation:

import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

def send_email_sendgrid(to_email: str, subject: str, html_content: str):
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("noreply@peoplerate.com")
    to_email = To(to_email)
    content = Content("text/html", html_content)
    mail = Mail(from_email, to_email, subject, content)
    
    response = sg.client.mail.send.post(request_body=mail.get())
    return response.status_code == 202
"""
