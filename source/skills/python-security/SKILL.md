---
name: python-security
description: Python security practices covering unsafe APIs (eval/exec/pickle), input validation, SQL injection prevention, crypto randomness, and safe subprocess/file handling. Use when writing Python code that touches user input, DB queries, web auth/sessions, XML parsing, serialization, or system commands.
---

# Python Security Checklist

## Dangerous Functions to Avoid
- **Never use** `eval()` with untrusted data
- **Never use** `exec()` with user input
- **Avoid** `pickle` module with untrusted data - use JSON instead
- **Avoid** `yaml.load()` - use `yaml.safe_load()` instead

## Cryptographic Randomness
- Use `secrets` module for cryptographic randomness (not `random`)
- Use `secrets.token_urlsafe()` for generating tokens
- Use `secrets.compare_digest()` for constant-time comparison

## Database Security
- **Always use parameterized queries** with SQLAlchemy or psycopg2
- Never build SQL queries with string formatting
- Apply least privilege to database users
- Enable database audit logging

## Session and Cookie Security
- Set `httponly=True` on sensitive cookies
- Set `secure=True` to enforce HTTPS-only cookies
- Set `samesite='Strict'` or `'Lax'` for CSRF protection
- Use secure session management (Flask-Session, Django sessions)

## XML Parsing Security
- Use `defusedxml` library instead of standard `xml` module
- Disable external entity processing to prevent XXE attacks
- Validate XML schemas before parsing

## Input Validation
- Validate all user input with allowlists
- Use type hints and Pydantic for data validation
- Sanitize input before using in system commands or SQL

## Path Traversal Prevention
- Use `pathlib.Path.resolve()` to normalize paths
- Validate that resolved paths stay within allowed directories
- Never construct file paths from user input without validation

## Command Injection Prevention
- **Avoid** `os.system()` and `subprocess.shell=True`
- Use `subprocess.run()` with list arguments (not shell strings)
- Validate and sanitize any input used in commands

## Static Analysis Tools
- Use `bandit` for security-focused static analysis
- Use `safety` to check for known vulnerabilities in dependencies
- Configure pre-commit hooks for automatic security checks

## Common Vulnerabilities to Prevent

### SQL Injection
```python
# WRONG - vulnerable to SQL injection
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# CORRECT - parameterized query
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

### Path Traversal
```python
# WRONG - vulnerable to directory traversal
with open(f"uploads/{filename}") as f:
    data = f.read()

# CORRECT - validate and normalize path
from pathlib import Path
base = Path("uploads").resolve()
filepath = (base / filename).resolve()
if not filepath.is_relative_to(base):
    raise ValueError("Invalid path")
with open(filepath) as f:
    data = f.read()
```

### Command Injection
```python
# WRONG - shell injection risk
os.system(f"convert {user_file} output.png")

# CORRECT - use list arguments
subprocess.run(["convert", user_file, "output.png"], check=True)
```

## Dependencies
- Pin dependency versions in `requirements.txt`
- Use `pip-audit` to scan for vulnerabilities
- Keep dependencies updated regularly
- Review security advisories for dependencies
