---
name: go-security
description: Go security practices for template safety, SQL parameterization, TLS/crypto usage, and secure input handling. Use when writing Go services, HTTP handlers, database access, auth flows, file path handling, or any crypto/TLS configuration.
---

# Go Security Checklist

## Template Security
- Use `html/template` package (not `text/template`) for HTML output
- HTML templates auto-escape content to prevent XSS
- Never use `text/template` for web content

## Database Security
- **Never use** `fmt.Sprintf()` to build SQL queries
- Use parameterized queries with database/sql
- Use prepared statements for repeated queries
- Apply least privilege to database connections

## Cryptographic Randomness
- Use `crypto/rand` (not `math/rand`) for security-critical randomness
- Use `crypto/rand.Read()` for generating tokens and keys
- Use `crypto/subtle.ConstantTimeCompare()` for comparing secrets

## TLS/SSL Security
- Validate certificate chains in TLS connections
- Don't set `InsecureSkipVerify: true` in production
- Use modern TLS versions (TLS 1.2+)
- Configure strong cipher suites

## Input Validation
- Validate all user input before processing
- Use `strconv` functions for type conversion with error checking
- Sanitize input used in system commands or queries
- Validate file paths to prevent directory traversal

## Error Handling
- Don't expose stack traces or internal errors to users
- Log detailed errors internally
- Return generic error messages to clients
- Use custom error types for better control

## Static Analysis Tools
- Use `gosec` for security-focused static analysis
- Use `go vet` to catch common mistakes
- Configure golangci-lint with security linters
- Run `go mod verify` to check dependencies

## Common Vulnerabilities to Prevent

### SQL Injection
```go
// WRONG - vulnerable to SQL injection
query := fmt.Sprintf("SELECT * FROM users WHERE id = %s", userId)
db.Query(query)

// CORRECT - parameterized query
db.Query("SELECT * FROM users WHERE id = ?", userId)
```

### Path Traversal
```go
// WRONG - vulnerable to directory traversal
filepath := "uploads/" + filename
data, _ := os.ReadFile(filepath)

// CORRECT - validate and clean path
import "path/filepath"
base := "/var/www/uploads"
fullpath := filepath.Join(base, filepath.Clean(filename))
if !strings.HasPrefix(fullpath, base) {
    return errors.New("invalid path")
}
data, err := os.ReadFile(fullpath)
```

### Command Injection
```go
// WRONG - shell injection risk
cmd := exec.Command("sh", "-c", "convert "+userFile+" output.png")

// CORRECT - use array arguments
cmd := exec.Command("convert", userFile, "output.png")
```

## Memory Safety
- Avoid unsafe package unless absolutely necessary
- Clear sensitive data from memory after use
- Use `defer` to ensure cleanup happens
- Be careful with slice and map capacities to avoid leaks

## Concurrency Safety
- Protect shared state with mutexes or channels
- Avoid data races (use `go build -race` to detect)
- Use `sync.Map` for concurrent map access
- Be careful with goroutine lifecycle management

## Dependencies
- Use `go mod verify` to verify dependencies
- Keep dependencies up to date with `go get -u`
- Review security advisories for dependencies
- Minimize dependency footprint
- Use `govulncheck` to scan for known vulnerabilities
