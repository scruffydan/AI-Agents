---
name: update-readme
description: Use when making code changes that affect user-facing behavior, before committing or pushing - reminds AI to check if README needs updates to stay in sync with implementation changes
---

# Update README Reminder

## Overview

Documentation drift is inevitable - code changes, README doesn't. This skill ensures the README stays current.

**Core principle:** If users need to know about the change, the README probably needs updating.

## The Gate Function

```
BEFORE claiming work is complete or committing:

1. ASSESS: What changed that users care about?
   - New features or commands
   - Changed configuration or setup steps
   - Breaking changes or API modifications
   - New dependencies or requirements
   - Removed or deprecated functionality

2. CHECK: Does README exist?
   ```sh
   ls -la README.md 2>/dev/null || ls -la readme.md 2>/dev/null
   ```

3. SCAN: Does README mention what changed?
   - Feature list includes new functionality?
   - Setup instructions still accurate?
   - API documentation matches code?
   - Examples still work?

4. DECIDE: Update needed?
   - YES: Edit README to reflect changes
   - NO: Proceed (but reconsider - did you miss something?)

5. VERIFY: If updated, check it renders correctly
```

## Common Changes Requiring README Updates

| Change Type | README Section to Update |
|-------------|-------------------------|
| New feature | Features, Usage, Examples |
| New command/flag | Usage, CLI Reference |
| Breaking change | Migration, Breaking Changes |
| New dependency | Installation, Requirements |
| Changed config | Configuration, Setup |
| API change | API Reference, Examples |
| New environment variable | Configuration |
| Removed feature | Remove from Features |

## Red Flags - STOP and Update README

- Added a feature not mentioned in README
- Changed how something works but docs show old way
- "Users will figure it out" (they won't)
- "It's obvious" (it's not to new users)
- "I'll document it later" (you won't)
- About to commit without checking README

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "It's just a small change" | Small changes confuse users too |
| "The code is self-documenting" | It's not. README needs words |
| "Users can read the code" | Users shouldn't need to |
| "I'll update docs in a separate PR" | Separate PRs often don't happen |
| "Nobody reads the README anyway" | They do when they're stuck |
| "This is internal only" | Is it? Really? |

## Quick Reference

**Always check README when:**
- Adding new CLI commands or flags
- Changing configuration format
- Adding/removing dependencies
- Modifying public APIs
- Changing setup/install steps
- Adding environment variables
- Deprecating features

**Quick check commands:**
```sh
# Does README exist?
test -f README.md && echo "README exists"

# Search for relevant terms
grep -n "feature-name" README.md

# Check if examples still work
grep -A5 "## Usage" README.md
```

## Examples

**Good:**
```
[Added new --verbose flag to CLI]
→ Scan README for CLI usage section
→ Add --verbose to flag list
→ Add example showing verbose output
→ Commit with "feat(cli): add --verbose flag and update README"
```

**Bad:**
```
[Changed default port from 8080 to 3000]
→ Commit with "change default port"
→ README still shows port 8080
→ Users try 8080, get connection refused
→ Wasted time, confused users
```

## Why This Matters

Out-of-date READMEs:
- Waste user time (trying broken instructions)
- Cause frustration ("why doesn't this work?")
- Reduce trust ("if docs are wrong, what else is?")
- Increase support burden (more questions)

## The Bottom Line

**README is part of the feature, not an afterthought.**

If the change matters enough to code, it matters enough to document.

Update the README before you commit.
