---
name: git-push
description: Pre-push checklist including README verification, tests, and commit quality checks
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
- ✅ New features added → Document usage
- ✅ New commands/scripts added → Add to documentation
- ✅ New configuration options → Document settings
- ✅ Breaking changes → Update examples and migration notes
- ✅ New dependencies → Update requirements section
- ✅ Installation process changed → Update install instructions
- ✅ API changes → Update API documentation

**README sections to review:**
- Installation/Setup
- Usage examples
- Configuration
- Requirements/Dependencies
- API reference (if applicable)
- Breaking changes/Migration guides

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

**Run tests:**
```sh
# Run test suite
npm test          # Node.js
pytest            # Python
go test ./...     # Go
./run_tests.sh    # Custom
```

**Check linting:**
```sh
npm run lint      # Node.js
pylint .          # Python
golangci-lint run # Go
```

**Verify build:**
```sh
npm run build     # Node.js
python setup.py build  # Python
go build ./...    # Go
```

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

### Push Rejected
```sh
# Pull and rebase
git pull --rebase origin main
git push
```

### Diverged Branches
```sh
# Check what diverged
git log HEAD..origin/main
git log origin/main..HEAD

# Rebase or merge as appropriate
git pull --rebase  # or git merge origin/main
```

### Accidental Secret Push

**If secrets were pushed:**
1. Immediately rotate/revoke the exposed credentials
2. Remove from history:
   ```sh
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/secret" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. Force push (if safe to do so)
4. Notify team/security

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
