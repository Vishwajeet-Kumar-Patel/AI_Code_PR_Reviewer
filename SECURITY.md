# Security Policy

## 🔒 Reporting Security Vulnerabilities

If you discover a security vulnerability, please email the maintainers directly. **Do not** open a public issue.

## 🛡️ Security Best Practices

### Secrets Management

**CRITICAL**: Never commit sensitive credentials to version control!

The following files should **NEVER** be committed:
- `.env` - Contains your actual API keys and secrets
- Any file with real credentials or tokens

### Setting Up Secrets Securely

1. **Copy the example file**:
   ```bash
   cp .env.example .env
   ```

2. **Generate strong secrets**:
   ```bash
   # For JWT_SECRET_KEY
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # Alternative using OpenSSL
   openssl rand -hex 32
   ```

3. **Fill in your actual API keys** in `.env`:
   - GitHub Token: https://github.com/settings/tokens (scopes: repo, read:org)
   - OpenAI API Key: https://platform.openai.com/api-keys
   - Gemini API Key: https://makersuite.google.com/app/apikey

4. **Verify .env is ignored**:
   ```bash
   git check-ignore .env
   # Should output: .env
   ```

### GitHub Actions Secrets

For CI/CD pipelines, add secrets via GitHub repository settings:

1. Go to repository **Settings** → **Secrets and variables** → **Actions**
2. Add the following secrets:
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `GEMINI_API_KEY` - Your Gemini API key (if using)
   - `GH_TOKEN` - GitHub Personal Access Token
   - `DOCKER_USERNAME` - Docker Hub username
   - `DOCKER_PASSWORD` - Docker Hub password/token

### What to Do If Secrets Are Exposed

If you accidentally commit secrets:

1. **Immediately revoke the exposed credentials**:
   - GitHub: https://github.com/settings/tokens
   - OpenAI: https://platform.openai.com/api-keys
   - Change database passwords

2. **Generate new credentials**:
   - Create new API keys
   - Generate new JWT secrets
   - Update environment variables

3. **Clean Git history** (if secrets were committed):
   ```bash
   # Remove from history using git-filter-repo
   git filter-repo --path .env --invert-paths
   
   # Force push (WARNING: Coordinate with team first!)
   git push origin --force --all
   ```

4. **Notify your team** and any affected users

### Production Security Checklist

- [ ] All secrets stored in `.env` file (not committed)
- [ ] Strong JWT_SECRET_KEY generated (minimum 32 characters)
- [ ] Database uses strong passwords
- [ ] DEBUG mode is set to `False`
- [ ] HTTPS enabled for all endpoints
- [ ] Rate limiting configured
- [ ] Security headers enabled
- [ ] Regular dependency updates
- [ ] API keys rotated periodically

### Environment-Specific Configuration

#### Development
```bash
DEBUG=True
LOG_LEVEL=DEBUG
```

#### Production
```bash
DEBUG=False
LOG_LEVEL=WARNING
# Use strong secrets!
JWT_SECRET_KEY=<strong-random-secret>
DATABASE_URL=<production-database-url>
```

## 🔍 Security Scanning

This project includes built-in security scanning:
- Secret detection in code reviews
- Dependency vulnerability scanning
- Code security analysis

## 📚 Additional Resources

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/secrets.html)

## 🆘 Emergency Contact

For urgent security issues, contact the project maintainers immediately.

---
**Remember**: Security is everyone's responsibility! 🛡️
