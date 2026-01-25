---
name: git-commit
description: Git commit workflow that analyzes the last 10 commits to learn and match repository naming conventions and commit message patterns
---

# Git Commit Skill

This skill ensures commit messages follow the repository's established conventions by analyzing recent commit history.

## Pre-Commit Workflow

### 1. Analyze Recent Commit History

**REQUIRED: Always run this BEFORE crafting commit message**

```sh
git log -10 --oneline --no-decorate
```

**Analyze for patterns:**
- Commit message format (conventional commits, custom format, free-form)
- Prefix/type usage (feat:, fix:, chore:, etc.)
- Capitalization style (sentence case, lowercase, title case)
- Length preferences (short, detailed)
- Scope usage (e.g., `feat(api):` vs `feat:`)
- Special conventions (emoji, ticket numbers, etc.)

### 2. Review Full Recent Messages

For deeper pattern analysis:

```sh
git log -10 --format="%h %s%n%b%n"
```

**Look for:**
- Multi-line message style
- Body content patterns
- Footer conventions (Closes #, Co-authored-by:, etc.)
- Breaking change indicators (BREAKING CHANGE:, !)
- Reference formats (issue numbers, PR links)

### 3. Match the Repository Style

**Use the EXACT same conventions as recent commits:**

If recent commits show:
```
feat: add user authentication
fix: resolve memory leak in cache
docs: update installation guide
```

Then use the same format:
```
<type>: <description>
```

If recent commits show:
```
feat(api): add webhook support
fix(auth): prevent token expiry edge case
```

Then include scopes:
```
<type>(<scope>): <description>
```

If recent commits show:
```
Add user authentication feature
Resolve memory leak in cache module
```

Then use free-form without prefixes.

### 4. Craft the Commit Message

**Follow repository conventions discovered in steps 1-3:**

```sh
git commit -m "type(scope): description"

# Or with body
git commit -m "type(scope): description" -m "
Detailed explanation of changes and reasoning.

Closes #123"
```

## Commit Message Best Practices

### Content Guidelines

**Focus on WHY, not WHAT:**
- ❌ "Changed login function"
- ✅ "Fix race condition in login flow"

**Be specific and actionable:**
- ❌ "Update code"
- ✅ "Optimize database query performance by 40%"

**Keep subject line concise:**
- Aim for 50-72 characters
- Match the length style of recent commits

**Use imperative mood (if repository does):**
- "Add feature" not "Added feature"
- "Fix bug" not "Fixes bug"
- Unless recent commits use past tense consistently

### Multi-line Messages

When changes are complex:

```sh
git commit -m "feat: add payment processing system" -m "
Integrate Stripe API for payment handling with:
- Webhook support for payment events
- Retry logic for failed transactions
- PCI compliance measures

Related to discussion in #456"
```

## Common Patterns

### Conventional Commits
```
feat: add new feature
fix: bug fix
docs: documentation
style: formatting
refactor: code restructuring
test: add tests
chore: maintenance
perf: performance
ci: CI/CD changes
build: build system
```

### With Scopes
```
feat(auth): add OAuth support
fix(api): handle null response
docs(readme): update installation
```

### With Breaking Changes
```
feat!: redesign API authentication

BREAKING CHANGE: Auth endpoints now require Bearer token
```

### With Issue References
```
fix: prevent duplicate submissions

Closes #123
Fixes #124
Related to #125
```

## Verification Before Commit

### Check Staged Changes
```sh
git status
git diff --cached
```

**Ensure:**
- Only intended files are staged
- No debug code or console.logs
- No sensitive data (secrets, keys, tokens)
- Changes are cohesive and atomic

### Review Commit Preview
```sh
# See what will be committed
git diff --cached --stat

# Verify commit message locally
git commit --dry-run
```

## Special Cases

### Amending Last Commit

**Only if:**
- Commit hasn't been pushed
- You need to fix typo or add forgotten file

```sh
git add forgotten-file.js
git commit --amend --no-edit

# Or to change message
git commit --amend -m "corrected message"
```

### Co-authored Commits

```sh
git commit -m "feat: implement shared feature" -m "
Co-authored-by: Name <email@example.com>"
```

### Empty Commits (rarely needed)

```sh
git commit --allow-empty -m "chore: trigger CI rebuild"
```

## Integration with Other Skills

**Before committing:**
- Review changes for quality
- Run tests if available
- Check for secrets (part of git-push skill)

**After committing:**
- See `git-push` skill for pre-push checklist

## Checklist

Before running `git commit`:
- [ ] Analyzed last 10 commits for conventions
- [ ] Identified repository's commit message pattern
- [ ] Matched format, style, and conventions
- [ ] Wrote clear, specific message explaining WHY
- [ ] Verified staged changes are correct
- [ ] No secrets or sensitive data in commit
- [ ] Message length matches repository style
- [ ] Used imperative/past tense matching repo style
