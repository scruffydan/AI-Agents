---
name: git-workflows
description: Git best practices including commit message guidelines, branching strategies, pull request workflows, and conflict resolution
---

# Git Workflows

Best practices and common patterns for working with Git in development workflows.

## Commit Message Guidelines

### Format
```
<type>: <short summary>

<optional detailed description>

<optional footer with issue references>
```

### Commit Types
- **feat**: New feature
- **fix**: Bug fix
- **refactor**: Code refactoring (no functional changes)
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **docs**: Documentation changes
- **style**: Code style/formatting changes
- **chore**: Maintenance tasks, dependency updates
- **ci**: CI/CD pipeline changes

### Examples
```
feat: add user authentication with JWT

Implement JWT-based authentication system with refresh tokens.
Includes login, logout, and token refresh endpoints.

Closes #123
```

```
fix: prevent memory leak in event listeners

Remove event listeners properly when components unmount.
```

## Branching Strategy

### Main Branches
- **main** (or **master**): Production-ready code
- **develop**: Integration branch for features

### Supporting Branches
- **feature/*** - New features (e.g., `feature/user-auth`)
- **bugfix/*** - Bug fixes (e.g., `bugfix/login-error`)
- **hotfix/*** - Urgent production fixes (e.g., `hotfix/security-patch`)
- **release/*** - Release preparation (e.g., `release/v1.2.0`)

### Branch Naming Conventions
```
feature/add-payment-processing
bugfix/fix-cart-total-calculation
hotfix/security-cve-2024-1234
release/v2.0.0
```

## Common Workflows

### Feature Development
```bash
# Create feature branch from develop/main
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: implement new feature"

# Push to remote
git push -u origin feature/new-feature

# Create pull request when ready
gh pr create --title "Add new feature" --body "Description..."
```

### Updating Your Branch
```bash
# Fetch latest changes
git fetch origin

# Rebase on main (keeps history clean)
git rebase origin/main

# Or merge (preserves branch history)
git merge origin/main
```

### Interactive Rebase (Clean Up Commits)
```bash
# Rebase last 3 commits
git rebase -i HEAD~3

# Options in interactive mode:
# pick = keep commit
# reword = change commit message
# squash = combine with previous commit
# drop = remove commit
```

### Fixing Mistakes

**Undo last commit (keep changes)**
```bash
git reset --soft HEAD~1
```

**Undo last commit (discard changes)**
```bash
git reset --hard HEAD~1
```

**Amend last commit**
```bash
git commit --amend
```

**Revert a pushed commit**
```bash
git revert <commit-hash>
```

## Pull Request Workflow

### Creating a PR
1. Ensure branch is up to date with base branch
2. Run tests and linting locally
3. Write clear PR title and description
4. Reference related issues
5. Request reviewers

### PR Description Template
```markdown
## Summary
Brief description of changes

## Changes
- Change 1
- Change 2

## Testing
How to test these changes

## Screenshots (if applicable)

## Related Issues
Closes #123
```

### Before Merging
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] No merge conflicts
- [ ] Branch up to date with base
- [ ] Documentation updated

## Best Practices

### Commits
- **Make atomic commits** - Each commit should be a logical unit
- **Commit often** - Don't wait until the end of the day
- **Write clear messages** - Future you will thank you
- **Test before committing** - Don't commit broken code

### Branches
- **Keep branches short-lived** - Merge frequently
- **Delete merged branches** - Clean up after merging
- **Update regularly** - Rebase/merge from main often
- **One branch per feature** - Don't mix unrelated changes

### General
- **Never force push to shared branches** - Especially main/develop
- **Use .gitignore** - Don't commit build artifacts, secrets, or IDE files
- **Review your own PR first** - Catch obvious issues before review
- **Keep commits focused** - One feature/fix per branch when possible

## Resolving Conflicts

```bash
# Pull latest changes
git pull origin main

# If conflicts occur, Git will mark them in files
# Look for conflict markers:
# <<<<<<< HEAD
# Your changes
# =======
# Their changes
# >>>>>>> branch-name

# Edit files to resolve conflicts
# Remove conflict markers
# Keep the correct code

# Stage resolved files
git add <resolved-files>

# Continue rebase (if rebasing)
git rebase --continue

# Or commit merge (if merging)
git commit
```

## Useful Git Commands

```bash
# View commit history
git log --oneline --graph --all

# See what changed in a commit
git show <commit-hash>

# Find which commit changed a line
git blame <file>

# Stash changes temporarily
git stash
git stash pop

# Cherry-pick a commit from another branch
git cherry-pick <commit-hash>

# View differences
git diff                    # Unstaged changes
git diff --staged          # Staged changes
git diff main..feature     # Between branches
```

## Git Safety Tips

- Always review `git status` before committing
- Use `git diff` to see what you're about to commit
- Double-check branch name before pushing
- Never commit sensitive data (use environment variables)
- Use pre-commit hooks to enforce standards
