---
name: git-push
description: You MUST use this when performing a git push. Pre-push checklist for README updates, tests/linters, commit hygiene, secret scanning, and branch/remote status. Use when preparing to run git push, reviewing a branch before publishing, or verifying release readiness.
---

# Git Push Checklist

Systematic checks to perform before pushing code to remote repositories.

## Pre-Push Verification

### 1. README Update Check
**CRITICAL: Verify README is current with changes**

Before pushing, check if README needs updates:

```sh
# Check if README exists
ls -la README.md 2>/dev/null
```

**Update README if:**
- New features, commands, or configuration changes
- Installation, dependencies, or requirements change
- Breaking changes or API changes

### 2. Commit Quality

**Review commit messages:**
```sh
git log origin/main..HEAD --oneline
```

Ensure commits:
- Follow conventional commits format (feat:, fix:, docs:, etc.)
- Have descriptive messages explaining "why" not "what"
- Are properly scoped and atomic
- Don't contain sensitive information (secrets, tokens, credentials)

### 3. Code Quality

- Run the project's tests
- Run linters/formatters if configured
- Verify build or packaging if applicable

### 4. Security Check

**Before pushing, verify:**
- ❌ No secrets in commits (.env, API keys, passwords)
- ❌ No sensitive data (credentials, tokens, private keys)
- ❌ No hardcoded passwords or tokens
- ✅ `.gitignore` includes sensitive files

**Search for potential secrets:**
```sh
git diff origin/main..HEAD | grep -i "password\|secret\|api_key\|token"
```

### 5. Branch Verification

**Check branch state:**
```sh
git status
git log origin/main..HEAD
```

**Verify:**
- On correct branch
- All changes committed
- No untracked files that should be committed
- Branch is up to date with remote base branch

### 6. Remote Check

**Before force pushing:**
```sh
git log origin/$(git branch --show-current)..HEAD
```

**Never force push if:**
- ❌ Branch is shared with others
- ❌ Branch is main/master
- ❌ Commits already pushed to remote

**Only force push if:**
- ✅ User explicitly requested it
- ✅ Branch is personal/feature branch
- ✅ You understand the consequences

## Push Commands

### Standard Push
```sh
git push
```

### First Push (set upstream)
```sh
git push -u origin branch-name
```

### Force Push (DANGEROUS - ask first)
```sh
# Only after explicit user permission
git push --force-with-lease
```

## Post-Push Verification

After pushing:
1. Verify CI/CD pipeline passes
2. Check pull request status (if applicable)
3. Verify deployment succeeded (if applicable)
4. Monitor for errors in production

## Common Issues

- For push rejections or diverged branches, rebase/merge per repo policy.
- If secrets were pushed, rotate credentials and remove from history.

## Checklist Summary

Before `git push`:
- [ ] README updated (if repo has one and changes warrant it)
- [ ] Tests passing
- [ ] Linting clean
- [ ] Build successful
- [ ] No secrets in commits
- [ ] Commit messages are clear
- [ ] On correct branch
- [ ] All intended changes committed
- [ ] CI/CD will pass (reasonable expectation)
