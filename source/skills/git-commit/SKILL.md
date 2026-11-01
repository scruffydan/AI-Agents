---
name: git-commit
description: Git commit workflow that analyzes recent history to match repo-specific message conventions. Use when you don't have recent commit history in context and need to determine the repository's commit message style, or when crafting commit messages that need to match existing conventions.
---

# Git Commit Skill

Inspect the working tree and preserve unrelated edits and untracked files. Follow
the user's and repository's authorization for commits. Use the history below
only when the relevant conventions are not already established in this session.

## Pre-Commit Workflow

### 1. Analyze Recent Commit History

**Run this when you don't have recent commit history in context**

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

## Verification and Commit

Before committing:

- Use `verification-before-completion` for relevant checks and `update-readme`
  for README and existing AGENTS.md accuracy. Reuse valid session evidence.
- Inspect the diff for unintended edits, debugging leftovers, and sensitive data.
- Stage only the intended paths and inspect `git diff --cached` before committing.
- Keep each commit focused and report its hash and verification results.

Do not add an approval step when the commit is already authorized. Amend or
rewrite history only within authorization. Pushing requires separate permission;
use `git-push` when a push is requested.
