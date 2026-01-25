---
name: shell-security
description: POSIX shell security best practices for sh-compatible scripts including variable quoting, command injection prevention, and safe file operations
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
- Use `mktemp` for creating secure temporary files
- Set restrictive permissions (600 or 700)
- Clean up temporary files in trap handlers

```sh
tmpfile=$(mktemp)
trap 'rm -f "$tmpfile"' EXIT INT TERM

# Or for maximum portability (mktemp may not exist on all systems)
tmpdir="${TMPDIR:-/tmp}"
tmpfile="$tmpdir/script.$$"
trap 'rm -f "$tmpfile"' EXIT INT TERM
touch "$tmpfile"
chmod 600 "$tmpfile"
```

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
```sh
# WRONG - user can access any file
cat "uploads/$filename"

# CORRECT - validate path stays in directory (POSIX-compatible)
# First check for path traversal attempts
case "$filename" in
    *..* | /* | *~* )
        echo "Invalid filename" >&2
        exit 1
        ;;
esac

# Resolve and validate (requires realpath utility)
if command -v realpath >/dev/null 2>&1; then
    realpath=$(realpath "uploads/$filename" 2>/dev/null) || exit 1
    case "$realpath" in
        /var/www/uploads/*)
            cat "$realpath"
            ;;
        *)
            echo "Invalid path" >&2
            exit 1
            ;;
    esac
else
    # Fallback without realpath - basic checks only
    cat "uploads/$filename"
fi
```

### Command Injection
```sh
# WRONG - user can inject commands
grep "$user_input" file.txt

# CORRECT - use -- and quotes
grep -- "$user_input" file.txt

# For maximum safety, validate input first
case "$user_input" in
    *[\;\&\|\>\<\`\$\(\)]*)
        echo "Invalid characters in input" >&2
        exit 1
        ;;
esac
```

### Environment Variable Attacks
```sh
# Set safe PATH (POSIX requires 'export' separate from assignment for portability)
PATH="/usr/local/bin:/usr/bin:/bin"
export PATH

# Unset dangerous variables
unset LD_PRELOAD LD_LIBRARY_PATH IFS

# Reset IFS to default if needed
IFS=' 	
'  # space, tab, newline
```

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
```sh
# Fail on pipe errors (NOT POSIX - bash/ksh only)
set -o pipefail  # Use only if #!/bin/bash

# POSIX alternative: check each command in pipeline explicitly
if ! command1 | command2 | command3; then
    echo "Pipeline failed" >&2
    exit 1
fi

# Or capture intermediate results to files
command1 > "$tmpfile1" || exit 1
command2 < "$tmpfile1" > "$tmpfile2" || exit 1
command3 < "$tmpfile2" || exit 1
```

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

### Bash-Only Features (NOT POSIX)
```sh
# DON'T USE (bash-only):
[[ "$var" == "value" ]]      # Use: [ "$var" = "value" ]
source script.sh              # Use: . script.sh
(( i++ ))                     # Use: i=$((i + 1))
$RANDOM                       # Use: external tool or /dev/urandom
${var^^}                      # Use: tr '[:lower:]' '[:upper:]'
${var,,}                      # Use: tr '[:upper:]' '[:lower:]'
[[ "$var" =~ regex ]]        # Use: expr or grep
```

### POSIX-Compatible Alternatives
```sh
# String comparison
[ "$var" = "value" ]          # POSIX (note: single =)

# Source a file
. ./script.sh                 # POSIX (note: dot, not source)

# Arithmetic
i=$((i + 1))                  # POSIX arithmetic expansion
: $((i += 1))                 # POSIX arithmetic with no-op

# Test for empty string
[ -z "$var" ]                 # POSIX (true if empty)
[ -n "$var" ]                 # POSIX (true if not empty)

# Multiple conditions
[ "$a" = "x" ] && [ "$b" = "y" ]    # AND
[ "$a" = "x" ] || [ "$b" = "y" ]    # OR
```

## Testing POSIX Compliance

```sh
# Test your script with different shells
sh script.sh      # POSIX sh
dash script.sh    # Debian/Ubuntu minimal shell
ash script.sh     # Alpine Linux shell
bash script.sh    # GNU bash

# Check for bash-isms
checkbashisms script.sh  # Debian devscripts package
shellcheck script.sh     # General shell linter
```

## Platform-Specific Considerations

### Linux vs BSD vs macOS
- **stat**: Different syntax across platforms
  ```sh
  # DON'T: stat -c '%Y' file  # Linux only
  # DO: use ls -l or find instead for portability
  ```
- **sed -i**: Different syntax
  ```sh
  # AVOID in-place editing across platforms
  # DO: Use temp file explicitly
  sed 's/old/new/g' file > "$tmpfile" && mv "$tmpfile" file
  ```
- **readlink -f**: Not available on macOS
  ```sh
  # AVOID: readlink -f
  # DO: Use pwd -P or realpath (if available)
  ```
