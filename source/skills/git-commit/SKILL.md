---
name: git-commit
description: Git commit workflow that analyzes recent history to match repo-specific message conventions. Use when you don't have recent commit history in context and need to determine the repository's commit message style, or when crafting commit messages that need to match existing conventions.
---

# Prepare and Make a Commit

Inspect `git status`, the working diff, and staged changes. Preserve unrelated
edits and untracked files. Follow the user's and repository's commit instructions.

If recent commit history is not already in context, run:

```sh
git log -10 --format="%h %s%n%b%n"
```

Match the repository's actual subject and body conventions, including free-form
subjects where used. Write a concise message explaining the change and its
purpose; do not impose conventional-commit prefixes on a repository without them.

Before committing:

- Use `verification-before-completion` for relevant checks and `update-readme`
  for README and existing AGENTS.md accuracy. Reuse valid session evidence.
- Inspect the diff for unintended edits, debugging leftovers, and sensitive data.
- Stage only the intended paths and inspect `git diff --cached` before committing.
- Keep each commit focused and report its hash and verification results.

Do not add an approval step when the commit is already authorized. Amend or
rewrite history only within authorization. Pushing requires separate permission;
use `git-push` when a push is requested.
