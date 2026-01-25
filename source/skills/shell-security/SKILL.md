---
name: shell-security
description: Shell and Bash security best practices including variable quoting, command injection prevention, and safe file operations
---

# Shell/Bash Security Checklist

## Variable Quoting
- **Always quote variables**: Use `"$var"` not `$var`
- Prevents word splitting and glob expansion
- Critical for file paths with spaces

```bash
# WRONG - breaks with spaces
rm $file

# CORRECT - handles spaces safely
rm "$file"
```

## Command Injection Prevention
- **Never use** `eval` with user input
- Avoid constructing commands from user data
- Use built-in commands when possible instead of external programs

## Option Parsing Safety
- Use `--` to end option parsing and prevent option injection
- Prevents files named `-rf` from being interpreted as options

```bash
# WRONG - vulnerable if file starts with -
rm $file

# CORRECT - treats everything after -- as arguments
rm -- "$file"
```

## Input Validation
- Validate input before passing to commands
- Use allowlists for expected values
- Sanitize or reject unexpected characters
- Check file paths resolve to expected directories

```bash
# Validate input
if [[ ! "$input" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "Invalid input"
    exit 1
fi
```

## Temporary Files
- Use `mktemp` for creating secure temporary files
- Set restrictive permissions (600 or 700)
- Clean up temporary files in trap handlers

```bash
tmpfile=$(mktemp)
trap 'rm -f "$tmpfile"' EXIT
```

## Secure File Operations
- Check if files exist before operations
- Use absolute paths when possible
- Set umask appropriately (e.g., `umask 077`)
- Verify file ownership and permissions

## Command Substitution
- Prefer `$(command)` over backticks
- Quote command substitution: `"$(command)"`
- Validate output before using

## Built-in Preference
- Prefer bash built-ins over external commands for security
- Built-ins: `[[`, `printf`, `read`, `source`
- Reduces attack surface from external binaries

## Common Vulnerabilities to Prevent

### Path Traversal
```bash
# WRONG - user can access any file
cat "uploads/$filename"

# CORRECT - validate path stays in directory
realpath=$(realpath "uploads/$filename")
if [[ "$realpath" != /var/www/uploads/* ]]; then
    echo "Invalid path"
    exit 1
fi
cat "$realpath"
```

### Command Injection
```bash
# WRONG - user can inject commands
grep "$user_input" file.txt

# CORRECT - use -- and quotes
grep -- "$user_input" file.txt
```

### Environment Variable Attacks
```bash
# Set safe PATH
export PATH="/usr/local/bin:/usr/bin:/bin"

# Unset dangerous variables
unset LD_PRELOAD LD_LIBRARY_PATH
```

## Shell Options for Security
```bash
# Exit on error
set -e

# Exit on undefined variable
set -u

# Fail on pipe errors
set -o pipefail

# Disable pathname expansion
set -f
```

## Logging and Debugging
- Don't log sensitive data (passwords, tokens)
- Use `set -x` carefully in production
- Redirect sensitive output to /dev/null when needed

## Script Execution
- Use `#!/usr/bin/env bash` for portability
- Check script is run with expected privileges
- Validate script hasn't been modified (checksums)
