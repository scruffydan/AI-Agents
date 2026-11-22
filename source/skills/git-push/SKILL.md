---
name: git-push
description: Check the outgoing commits, branch, remote, and readiness to publish, then push. Use before a git push.
---

# Git Push

Identify the push destination repository and its actual default branch, then
apply the push authorization rules from your instructions to every destination
ref, including pushes from a local topic branch. Inspect the working tree without
disturbing unrelated changes.

Before pushing:

- Apply the push or PR guidance in `verification-before-completion`, as applicable,
  and use `update-readme` when needed. Pushing does not itself require new test runs.
- Use `git-commit` for repository-specific message conventions. Free-form subjects
  are valid when the repository uses them. Preserve existing commits when checking
  message style.
- Identify the source commit and exact destination refs. For each ref, inspect
  the outgoing commits and diff for unintended files and sensitive data.
  Use an available local secret scanner if appropriate, without printing secrets.
- Confirm that intended changes are committed and assess divergence before
  publishing. Resolve rejection or divergence under repository policy; destructive
  history changes need explicit authorization.

For a single-branch push, name the verified remote and one explicit refspec.
For example, from the checked topic branch use
`git push --no-follow-tags origin HEAD:refs/heads/my-topic`. A bare `git push`
can select additional refs or a different remote through configuration. If
multiple refs are in scope, specify each verified refspec explicitly.

When a force push is explicitly authorized, use
`--force-with-lease=<destination-ref>:<expected-sha>` with the observed remote
SHA for that ref.

Report the push result. Check applicable CI or PR status within the requested
scope and use the environment's monitoring tools when waiting is requested.
A successful push alone does not establish that tests or deployment succeeded.
