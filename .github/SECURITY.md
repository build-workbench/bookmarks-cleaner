# Security Policy

## Supported Versions

The following versions of CleanBook are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.x.x   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within CleanBook, please send an email to the repository owner. All security vulnerabilities will be promptly addressed.

**Please do not open public issues for security vulnerabilities.**

### Reporting Process

1. **Email**: Send details to the repository maintainer via GitHub
2. **Response Time**: You will receive an acknowledgment within 48 hours
3. **Updates**: We will keep you informed about our progress on the fix
4. **Disclosure**: Once the vulnerability is fixed, we will coordinate disclosure with you

### What to Include

When reporting a vulnerability, please include:

- A description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fix (if any)
- Your disclosure preferences

## Security Measures

This project implements the following security practices:

- **Dependency Scanning**: Regular automated scans for vulnerable dependencies
- **Code Review**: All changes require code review before merging
- **Branch Protection**: Protected branches prevent direct pushes to main/master
- **Security Testing**: Bandit and safety checks in CI pipeline

## Known Security Considerations

### API Keys and Secrets

- CleanBook supports optional LLM features that require API keys
- **Never commit API keys to the repository**
- Use environment variables or `.env` files (ignored by git)
- See `.env.example` for the required environment variables

### Local Data Processing

- CleanBook is designed as an offline-first tool
- Bookmark data is processed locally and never sent to external services
- LLM features only send data to your configured provider (OpenAI, etc.)

## Security Best Practices for Users

1. Keep your Python dependencies updated
2. Review configuration files before running
3. Use virtual environments to isolate dependencies
4. Report any suspicious behavior immediately
