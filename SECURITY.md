# Security Implementation Guide

## Overview
PeopleRate implements multiple layers of security to protect user data and prevent common web vulnerabilities.

## 📋 Security Checklist

### ✅ Implemented Features
- [x] JWT-based authentication with bcrypt password hashing
- [x] Rate limiting on critical endpoints (registration, login, reviews)
- [x] Security headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, HSTS)
- [x] CORS middleware with configurable origins
- [x] Content moderation (profanity filtering, spam detection)
- [x] Input sanitization utilities (security_utils.py)
- [x] Password strength validation
- [x] Email format validation
- [x] Username validation and blacklisting
- [x] SQL/NoSQL injection protection (Pydantic validation)
- [x] HTTPS enforcement headers
- [x] Sensitive data encryption (passwords with bcrypt)

### ⚠️ Production Requirements
- [ ] Change SECRET_KEY to a cryptographically secure value
- [ ] Set ENVIRONMENT=production in .env
- [ ] Update CORS_ORIGINS to production domains only
- [ ] Enable SESSION_COOKIE_SECURE=true (requires HTTPS)
- [ ] Configure SendGrid for email (or remove email features)
- [ ] Set up MongoDB Atlas with IP whitelist
- [ ] Enable database encryption at rest
- [ ] Configure backup strategy
- [ ] Set up monitoring and alerting
- [ ] Review and lawyer-approve ToS and Privacy Policy

## 🔐 Authentication & Authorization

### JWT Token Security
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Expiration**: 30 minutes (configurable)
- **Secret Key**: Must be changed before production
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(64))"
  ```
- **Token Location**: HTTP Authorization header (Bearer token)
- **Protection**: No sensitive data in payload

### Password Security
- **Hashing**: bcrypt with automatic salt generation
- **Minimum Length**: 8 characters
- **Complexity Requirements**:
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one digit
  - Optional special character
- **Storage**: Never stored in plain text
- **Transmission**: Only over HTTPS in production

### Session Management
- **Stateless**: JWT tokens (no server-side sessions)
- **Cookie Security**: Secure flag in production, HttpOnly recommended
- **CSRF Protection**: Consider adding CSRF tokens for forms

## 🛡️ Input Validation & Sanitization

### Implemented in `security_utils.py`
1. **HTML Sanitization** (`sanitize_html`)
   - Strips all HTML tags using bleach library
   - Prevents XSS (Cross-Site Scripting) attacks

2. **Input Sanitization** (`sanitize_input`)
   - Removes HTML
   - Trims whitespace
   - Enforces length limits

3. **Email Validation** (`validate_email_format`)
   - RFC-compliant format checking
   - Max 320 characters
   - Detects suspicious patterns

4. **Username Validation** (`validate_username`)
   - Length: 3-30 characters
   - Allowed: alphanumeric, underscore, hyphen
   - Must start with letter/number
   - Blacklist of reserved words

5. **Password Strength** (`validate_password_strength`)
   - Complexity requirements
   - Common password detection
   - Length constraints (8-128 chars)

6. **URL Sanitization** (`sanitize_url`)
   - Protocol validation (http/https only)
   - XSS prevention (blocks javascript:, data: URLs)
   - Length limit (2048 chars)

7. **Social Media URL Validation** (`validate_social_media_url`)
   - Platform-specific format validation
   - LinkedIn, Instagram, Facebook, Twitter, GitHub

8. **Search Query Sanitization** (`sanitize_search_query`)
   - Removes regex special characters
   - Prevents injection attacks
   - Length limit (200 chars)

## 🚫 Rate Limiting

### Configured Endpoints
- **Registration**: 5 requests/hour (prevents spam accounts)
- **Login**: 10 requests/minute (prevents brute force)
- **Review Creation**: 5 requests/hour (prevents spam reviews)
- **Flag Content**: 10 requests/hour (prevents abuse)
- **Scam Vote**: 3 requests/hour (prevents manipulation)

### Implementation
- **Library**: slowapi (Python port of Flask-Limiter)
- **Key**: Client IP address
- **Storage**: In-memory (consider Redis for production)
- **Response**: HTTP 429 (Too Many Requests)

## 🔒 Security Headers

### Implemented Headers
```python
X-Content-Type-Options: nosniff  # Prevents MIME sniffing
X-Frame-Options: DENY  # Prevents clickjacking
X-XSS-Protection: 1; mode=block  # IE/Edge XSS filter
Strict-Transport-Security: max-age=31536000; includeSubDomains  # HTTPS enforcement
```

### Recommended Additional Headers (Future)
```python
Content-Security-Policy: default-src 'self'  # CSP to prevent XSS
Referrer-Policy: no-referrer  # Privacy protection
Permissions-Policy: geolocation=(), microphone=(), camera=()  # Feature restrictions
```

## 🌐 CORS (Cross-Origin Resource Sharing)

### Development
- **Allowed Origins**: `*` (all origins)
- **Credentials**: Allowed
- **Methods**: All
- **Headers**: All

### Production
- **Allowed Origins**: Specific domains only (set in CORS_ORIGINS env var)
- **Example**: `https://peoplerate.com,https://www.peoplerate.com`
- **Credentials**: Allowed (for cookie auth if added)
- **Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Headers**: Specific headers only

## 🗄️ Database Security

### MongoDB Atlas
- **Connection**: TLS/SSL encrypted
- **Authentication**: Username/password
- **IP Whitelist**: Configure in MongoDB Atlas dashboard
- **Encryption at Rest**: Enable in MongoDB Atlas
- **Backups**: Automated daily backups

### Query Security
- **Injection Protection**: Pydantic model validation
- **Parameterized Queries**: Beanie ODM handles escaping
- **Input Validation**: All inputs validated before database operations

## 📧 Email Security

### Current Implementation (MVP)
- **File-based**: Emails saved to `verification_emails/` directory
- **Tokens**: Cryptographically secure (secrets module)
- **Expiration**: 24 hours for verification, 1 hour for password reset

### Production (SendGrid)
- **API Key**: Store in environment variable
- **SPF/DKIM**: Configure in SendGrid
- **Rate Limiting**: SendGrid built-in
- **Link Security**: HTTPS only, token-based

## 🛠️ Content Moderation

### Features
1. **Profanity Filter** (better-profanity library)
   - Automatic censoring with ***
   - Severity detection
   - Expandable word list

2. **Spam Detection**
   - Excessive capitalization (>70%)
   - URL detection
   - Number spam (10+ digits)
   - Pattern matching

3. **Auto-Flagging**
   - Content flagged for manual review
   - High profanity
   - Spam patterns

## 🔍 Monitoring & Logging

### Current Logging
- **Level**: INFO
- **Format**: Structured logging with logger
- **Location**: Console (stdout)

### Production Recommendations
- **Centralized Logging**: Sentry, Papertrail, or CloudWatch
- **Log Levels**: 
  - ERROR: Authentication failures, exceptions
  - WARNING: Rate limit hits, suspicious activity
  - INFO: Normal operations
- **Sensitive Data**: Never log passwords, tokens, or personal info
- **Retention**: 30-90 days for compliance

### Security Events to Monitor
- Failed login attempts (potential brute force)
- Rate limit violations
- Content flagging spikes
- Unusual API patterns
- Database query errors
- Email delivery failures

## 🚨 Incident Response

### Data Breach Protocol
1. **Detection**: Monitoring alerts or user reports
2. **Containment**: Isolate affected systems
3. **Investigation**: Determine scope and impact
4. **Notification**: Email affected users within 72 hours (Privacy Policy commitment)
5. **Remediation**: Fix vulnerability, rotate keys
6. **Documentation**: Record incident details
7. **Legal Compliance**: Report to authorities as required by IT Act 2000

### Contacts
- **Technical Lead**: [Your Email]
- **Legal/Compliance**: legal@peoplerate.com
- **DPO**: dpo@peoplerate.com

## 🔄 Security Updates

### Regular Tasks
- [ ] Monthly: Review security logs
- [ ] Monthly: Update dependencies (security patches)
- [ ] Quarterly: Penetration testing
- [ ] Quarterly: Review access controls
- [ ] Annually: Security audit
- [ ] Annually: Update legal documents

### Dependency Updates
```bash
# Check for security vulnerabilities
pip install safety
safety check

# Update dependencies
pip list --outdated
pip install --upgrade [package]
```

## 📚 Additional Resources

### References
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [India IT Act 2000](https://www.meity.gov.in/content/information-technology-act)
- [GDPR Compliance](https://gdpr.eu/)
- [MongoDB Security](https://docs.mongodb.com/manual/security/)

### Tools
- **Security Scanning**: Bandit (Python), Snyk
- **Dependency Check**: Safety, pip-audit
- **Penetration Testing**: OWASP ZAP, Burp Suite
- **API Testing**: Postman, Thunder Client

## 🎯 Production Deployment Checklist

### Pre-Deployment
- [ ] Generate and set new SECRET_KEY
- [ ] Set ENVIRONMENT=production
- [ ] Configure production CORS_ORIGINS
- [ ] Set up MongoDB Atlas with IP whitelist
- [ ] Configure SendGrid (or remove email features)
- [ ] Enable HTTPS (Render.com provides this)
- [ ] Set SESSION_COOKIE_SECURE=true
- [ ] Review all environment variables
- [ ] Remove debug/development code
- [ ] Test all security features

### Post-Deployment
- [ ] Verify HTTPS working
- [ ] Test authentication flow
- [ ] Verify rate limiting active
- [ ] Check security headers
- [ ] Test content moderation
- [ ] Verify email sending (or mock)
- [ ] Monitor logs for errors
- [ ] Test from external network
- [ ] Run security scan
- [ ] Document deployment

### Ongoing
- [ ] Monitor error rates
- [ ] Review security logs weekly
- [ ] Update dependencies monthly
- [ ] Backup database regularly
- [ ] Renew SSL certificates (auto with Render)
- [ ] Review access logs for anomalies

---

**Last Updated**: November 28, 2024  
**Version**: 1.0 (MVP Launch)  
**Contact**: security@peoplerate.com
