# Security Best Practices

## Input Validation and Sanitization

### Validate All Input
- Never trust user input
- Validate on both client and server side
- Use whitelisting over blacklisting

```python
# Python example
def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

### SQL Injection Prevention
- Use parameterized queries
- Use ORM frameworks
- Never concatenate SQL strings with user input

```python
# Good - Parameterized
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# Avoid - String concatenation
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

### XSS Prevention
- Escape output
- Use Content Security Policy
- Sanitize HTML input

```javascript
// Good - Use textContent
element.textContent = userInput;

// Avoid - innerHTML with unsanitized input
element.innerHTML = userInput;
```

## Authentication and Authorization

### Password Security
- Use strong hashing algorithms (bcrypt, Argon2)
- Never store passwords in plain text
- Implement password complexity requirements
- Use multi-factor authentication

```python
import bcrypt

# Hash password
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# Verify password
if bcrypt.checkpw(password.encode(), hashed):
    # Password is correct
    pass
```

### Session Management
- Use secure session IDs
- Implement session timeouts
- Regenerate session IDs after login
- Use HTTPS for session cookies

```python
# Flask example
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
```

### JWT Best Practices
- Use strong signing algorithms (RS256)
- Keep tokens short-lived
- Store tokens securely
- Validate all token claims

## Secrets Management

### Environment Variables
- Store secrets in environment variables
- Use secret management services (AWS Secrets Manager, HashiCorp Vault)
- Never commit secrets to version control

```python
import os

# Good
api_key = os.getenv('API_KEY')
if not api_key:
    raise ValueError('API_KEY not set')

# Avoid
api_key = "hardcoded_secret_123"
```

### .gitignore
```
# Add to .gitignore
.env
.env.local
secrets/
*.key
*.pem
config/secrets.yml
```

## Cryptography

### Use Strong Algorithms
- AES-256 for encryption
- SHA-256 or SHA-3 for hashing
- RSA-2048+ or ECC for asymmetric crypto

```python
from cryptography.fernet import Fernet

# Generate key
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt
encrypted = cipher.encrypt(b"sensitive data")

# Decrypt
decrypted = cipher.decrypt(encrypted)
```

### Avoid Weak Crypto
- Don't use MD5 for security
- Don't use SHA-1 for new applications
- Don't use DES or 3DES
- Don't use ECB mode

## API Security

### Rate Limiting
- Implement rate limiting on all APIs
- Use different limits for authenticated vs anonymous
- Return appropriate HTTP status codes (429)

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["200 per day", "50 per hour"]
)

@app.route("/api/endpoint")
@limiter.limit("10 per minute")
def api_endpoint():
    return {"data": "response"}
```

### CORS Configuration
- Configure CORS properly
- Don't use wildcard (*) in production
- Specify exact allowed origins

```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": ["https://trusted-domain.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

### API Authentication
- Use API keys for service-to-service
- Use OAuth 2.0 for user authentication
- Implement request signing for sensitive operations

## File Upload Security

### Validate File Types
- Check file extensions
- Validate MIME types
- Scan files for malware
- Limit file sizes

```python
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Check file size
if len(file.read()) > MAX_FILE_SIZE:
    raise ValueError('File too large')
```

### Secure File Storage
- Store files outside web root
- Use random filenames
- Set appropriate file permissions

```python
import uuid
from werkzeug.utils import secure_filename

# Generate safe filename
original_filename = secure_filename(file.filename)
unique_filename = f"{uuid.uuid4()}_{original_filename}"
file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
```

## Dependency Management

### Keep Dependencies Updated
- Regularly update dependencies
- Monitor security advisories
- Use automated tools (Dependabot, Snyk)

### Audit Dependencies
```bash
# Python
pip-audit

# Node.js
npm audit
npm audit fix

# Check for vulnerabilities
safety check
```

## Logging and Monitoring

### Secure Logging
- Don't log sensitive data
- Sanitize log messages
- Implement log rotation
- Monitor logs for security events

```python
import logging

logger = logging.getLogger(__name__)

# Good - Don't log sensitive data
logger.info(f"User login: {username}")

# Avoid - Logging passwords
logger.info(f"Login attempt: {username}:{password}")
```

### Security Monitoring
- Monitor failed login attempts
- Track unusual access patterns
- Set up alerts for security events
- Implement intrusion detection

## HTTPS and TLS

### Always Use HTTPS
- Enforce HTTPS in production
- Use HSTS headers
- Use strong TLS configurations

```python
# Flask - Force HTTPS
from flask_talisman import Talisman

Talisman(app, force_https=True)
```

### Certificate Management
- Use valid SSL/TLS certificates
- Implement certificate pinning for mobile apps
- Monitor certificate expiration

## Error Handling

### Don't Leak Information
- Use generic error messages for users
- Log detailed errors server-side
- Don't expose stack traces in production

```python
try:
    # Risky operation
    result = perform_database_query()
except Exception as e:
    # Log detailed error
    logger.error(f"Database error: {str(e)}", exc_info=True)
    
    # Return generic error to user
    return {"error": "An error occurred. Please try again."}, 500
```

## Common Vulnerabilities (OWASP Top 10)

### A01: Broken Access Control
- Implement proper authorization checks
- Use role-based access control (RBAC)
- Validate user permissions on every request

### A02: Cryptographic Failures
- Protect data in transit and at rest
- Use strong encryption
- Properly manage encryption keys

### A03: Injection
- Use parameterized queries
- Validate and sanitize all input
- Use ORM frameworks

### A04: Insecure Design
- Threat modeling
- Secure design principles
- Security requirements

### A05: Security Misconfiguration
- Harden all configurations
- Disable unnecessary features
- Keep software updated

### A06: Vulnerable Components
- Track component versions
- Regular security updates
- Remove unused dependencies

### A07: Authentication Failures
- Implement MFA
- Strong password policies
- Secure session management

### A08: Data Integrity Failures
- Verify software signatures
- Use integrity checks
- Secure CI/CD pipelines

### A09: Logging Failures
- Log security events
- Monitor logs
- Protect log data

### A10: SSRF
- Validate URLs
- Use allowlists
- Network segmentation

## Security Checklist

- [ ] All user input is validated and sanitized
- [ ] Passwords are hashed with strong algorithms
- [ ] Secrets are not hardcoded
- [ ] HTTPS is enforced
- [ ] SQL injection prevention in place
- [ ] XSS prevention measures implemented
- [ ] CSRF protection enabled
- [ ] Rate limiting configured
- [ ] Security headers set
- [ ] Dependencies are up to date
- [ ] Security logging enabled
- [ ] Error messages don't leak information
- [ ] File uploads are validated
- [ ] Authentication and authorization working correctly
- [ ] Security tests written and passing
