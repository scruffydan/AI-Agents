---
name: sql-security
description: SQL security best practices including parameterized queries, injection prevention, least privilege, and ORM security patterns
---

# SQL Security Checklist

## Parameterized Queries
- **Always use parameterized queries** (prepared statements)
- Never concatenate user input into SQL strings
- Use ORM query builders correctly

```sql
-- WRONG - vulnerable to SQL injection
SELECT * FROM users WHERE email = '" + user_email + "'

-- CORRECT - parameterized query
SELECT * FROM users WHERE email = ?
```

## Least Privilege Principle
- Grant minimum necessary permissions to database users
- Use separate accounts for different application components
- Never use root/admin accounts for application access
- Revoke unnecessary privileges regularly

## Data Encryption
- Encrypt sensitive columns (PII, financial data, passwords)
- Use strong encryption algorithms (AES-256)
- Store encryption keys securely (separate from database)
- Use database-level encryption features when available

## Audit Logging
- Enable audit logging for sensitive operations
- Log authentication attempts (success and failure)
- Log data access for sensitive tables
- Retain logs according to compliance requirements

## Query Best Practices
- Avoid `SELECT *` in production code - specify columns explicitly
- Use LIMIT clauses to prevent resource exhaustion
- Validate input data types before queries
- Use stored procedures for complex operations

## Connection Security
- Use TLS/SSL for database connections
- Use connection pooling with authentication
- Rotate database credentials regularly
- Use connection string encryption

## Injection Prevention Patterns

### SQL Injection
```sql
-- WRONG - concatenation
cursor.execute("SELECT * FROM users WHERE id = " + user_id)

-- CORRECT - parameterized
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

### UNION-based Injection
- Limit query results to expected types
- Validate expected result structure
- Use allowlists for column names and table names

### Blind SQL Injection
- Implement rate limiting on queries
- Use generic error messages
- Monitor for timing attacks

## ORM Security
- Understand how your ORM generates SQL
- Avoid raw SQL queries when possible
- Validate data before passing to ORM
- Use ORM's built-in sanitization features

```python
# WRONG - raw SQL vulnerable to injection
User.objects.raw("SELECT * FROM users WHERE name = '%s'" % name)

# CORRECT - use ORM query methods
User.objects.filter(name=name)
```

## Database Configuration
- Disable unnecessary features and functions
- Remove sample databases and default accounts
- Use strong authentication mechanisms
- Keep database software updated

## Common SQL Injection Patterns to Block
- `' OR '1'='1` - authentication bypass
- `'; DROP TABLE users--` - data destruction
- `UNION SELECT` - data exfiltration
- Time-based blind injection patterns

## Protection Layers
1. **Input Validation** - Validate before query
2. **Parameterized Queries** - Use placeholders
3. **Least Privilege** - Minimal database permissions
4. **WAF Rules** - Web Application Firewall patterns
5. **Monitoring** - Detect anomalous queries

## Stored Procedures Security
- Validate input parameters
- Use parameterized statements inside procedures
- Grant EXECUTE-only permissions
- Avoid dynamic SQL within procedures

## NoSQL Injection (MongoDB, etc.)
- Validate input types (prevent object injection)
- Use parameterized queries in NoSQL drivers
- Sanitize regex patterns from user input
- Use allowlists for operators and field names
