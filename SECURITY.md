# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| latest  | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within FreateOJ, please send an email to **freatevietnam@gmail.com**. All security vulnerabilities will be promptly addressed.

**Please do NOT report security vulnerabilities through public GitHub issues.**

### What to include

When reporting a vulnerability, please include:

- A description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if any)

### Response timeline

- **Acknowledgment**: within 48 hours
- **Initial assessment**: within 1 week
- **Fix or mitigation**: depends on severity

## Security Best Practices

When deploying FreateOJ:

- Use HTTPS in production
- Set `DEBUG = False`
- Use a strong `SECRET_KEY`
- Keep dependencies updated
- Use PostgreSQL (not SQLite) for production
- Configure proper `ALLOWED_HOSTS`
- Set up proper caching (Redis/memcached) for judge sync
