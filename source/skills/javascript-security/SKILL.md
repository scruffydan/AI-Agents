---
name: javascript-security
description: JavaScript and TypeScript security best practices including XSS prevention, CSP headers, input validation, and common vulnerability patterns
---

# JavaScript/TypeScript Security Checklist

## Comparison Operators
- Use `===` not `==` for comparisons to avoid type coercion vulnerabilities

## Dangerous Functions to Avoid
- **Never use** `eval()` - allows arbitrary code execution
- **Never use** `Function()` constructor with user input
- **Avoid** `innerHTML` - use `textContent` or sanitize with DOMPurify

## React-Specific Security
- Sanitize before using `dangerouslySetInnerHTML`
- Always validate and escape user input before rendering
- Use proper prop validation

## Security Headers
- Implement Content Security Policy (CSP) headers
- Set `X-Frame-Options`, `X-Content-Type-Options`, `Strict-Transport-Security`

## Input Validation
- Validate and sanitize ALL user input on both client and server
- Use allowlists (not denylists) for input validation
- Escape output based on context (HTML, JavaScript, URL)

## Linting and Static Analysis
- Use `eslint-plugin-security` for automated security checks
- Configure ESLint rules for security best practices
- Run security audits with `npm audit` or `yarn audit`

## Authentication & Session Management
- Use `httpOnly` flag for sensitive cookies
- Set `secure` flag to enforce HTTPS-only cookies
- Implement `SameSite` attribute for CSRF protection
- Use secure session management libraries

## Common Vulnerabilities to Prevent

### XSS (Cross-Site Scripting)
- Escape user content before rendering
- Use templating engines with auto-escaping
- Validate and sanitize URLs before using in `href` or `src`

### Prototype Pollution
- Avoid using `Object.assign()` or spread with untrusted objects
- Use `Object.create(null)` for dictionaries
- Validate object keys before access

### Regular Expression DoS (ReDoS)
- Avoid complex regex patterns with user input
- Use regex timeouts when available
- Test regex patterns for catastrophic backtracking

## Dependencies
- Keep dependencies up to date
- Use `npm audit fix` or `yarn audit` regularly
- Review dependency security advisories
- Minimize dependency footprint
