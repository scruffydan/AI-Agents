---
name: shell-security
description: POSIX sh security guidance for safe quoting, option handling, command injection prevention, and file operations. Use when writing shell/bash scripts, handling user input, paths with spaces, temporary files, subprocess execution, or any command construction in a shell.
---

# POSIX Shell Security Checklist

This guide focuses on **POSIX sh-compatible** security practices that work across all Unix shells (sh, bash, dash, ash, etc.).

## Variable Quoting
- **Always quote variables**: Use `"$var"` not `$var`
- Prevents word splitting and glob expansion
- Critical for file paths with spaces

```sh
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

```sh
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

```sh
# POSIX-compatible input validation using case/expr
case "$input" in
    *[!a-zA-Z0-9_-]*)
        echo "Invalid input" >&2
        exit 1
        ;;
esac

# Or using expr for pattern matching
if ! expr "$input" : '^[a-zA-Z0-9_-]*$' >/dev/null; then
    echo "Invalid input" >&2
    exit 1
fi
```

## Temporary Files
- Use `mktemp` for secure temp files
- Set restrictive permissions (600 or 700)
- Clean up temp files in trap handlers

## Secure File Operations
- Check if files exist before operations
- Use absolute paths when possible
- Set umask appropriately (e.g., `umask 077`)
- Verify file ownership and permissions

## Command Substitution
- Prefer `$(command)` over backticks (more readable, nestable)
- Quote command substitution: `"$(command)"`
- Validate output before using

## Built-in Preference
- Prefer shell built-ins over external commands for security
- POSIX built-ins: `test` (or `[`), `printf`, `read`, `:`, `set`
- Reduces attack surface from external binaries
- **Avoid bash-isms**: `[[`, `source` (use `.` instead), `((` arithmetic

## Common Vulnerabilities to Prevent

### Path Traversal
- Reject `..`, absolute paths, and unexpected prefixes
- Validate resolved paths stay within the allowed directory

### Command Injection
- Use `--` and quotes
- Validate or reject metacharacters in user input

### Environment Variable Attacks
- Set a safe `PATH`
- Unset `LD_PRELOAD`, `LD_LIBRARY_PATH`, and `IFS`

## Shell Options for Security

### POSIX-Compatible Options
```sh
# Exit on error (errexit)
set -e

# Exit on undefined variable (nounset)
set -u

# Disable pathname expansion (noglob)
set -f
```

### Non-POSIX Options (bash/ksh only)
- `set -o pipefail` (use only with `#!/bin/bash`)

### Strict Mode (POSIX)
```sh
#!/bin/sh
set -eu  # Exit on error, exit on undefined variable

# Note: -o pipefail is NOT POSIX and will fail in dash, ash, etc.
```

## Logging and Debugging
- Don't log sensitive data (passwords, tokens)
- Use `set -x` carefully in production
- Redirect sensitive output to /dev/null when needed

## Script Execution
- Use `#!/bin/sh` for maximum portability across Unix systems
- Use `#!/usr/bin/env sh` if script needs to find sh in PATH
- **Only use** `#!/bin/bash` if you need bash-specific features
- Check script is run with expected privileges
- Validate script hasn't been modified (checksums)

## POSIX vs Bash: What to Avoid

- Avoid bash-only features like `[[ ]]`, `source`, `(( ))`, `$RANDOM`, and `=~`
- Prefer POSIX forms: `[ ]`, `.`, `$(( ))`, and `case`/`expr`

## Testing POSIX Compliance

- Test with `sh`, `dash`, `ash`, and `bash` where available
- Use `checkbashisms` or `shellcheck` to detect bash-isms

## Platform-Specific Considerations

- `stat`, `sed -i`, and `readlink -f` vary across platforms; prefer portable alternatives
