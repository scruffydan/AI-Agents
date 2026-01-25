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

```
<type>(<scope>): <description>
```

If commits are free-form, use the same free-form style without prefixes.

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
git commit -m "feat: add payment processing" -m "
Explain why, impact, and any references."
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

- Amend only if not pushed and fixing a typo/forgotten file.
- Add co-authors in commit body when needed.
- Use empty commits only if explicitly required.

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
