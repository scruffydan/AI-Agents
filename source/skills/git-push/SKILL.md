---
name: git-push
description: Use before an authorized git push to check the outgoing commits, branch, remote, and readiness to publish.
---

# Git Push

Push only when requested or already authorized. Inspect the working tree and the
intended branch and remote without disturbing unrelated changes.

Before pushing:

- Use `update-readme` for README and existing AGENTS.md accuracy.
- Use `verification-before-completion` for relevant checks and their evidence.
  Reuse valid checks on unchanged inputs; do not rerun them just because this
  skill is loaded.
- Use `git-commit` for repository-specific message conventions. Free-form subjects
  are valid when the repository uses them; do not impose conventional commits or
  rewrite existing commits just to change their style.
- Identify the actual destination and base branch; do not assume `origin/main`.
  Inspect the outgoing commits and diff for unintended files and sensitive data.
  Use an available local secret scanner if appropriate, without printing secrets.
- Confirm that intended changes are committed and assess divergence before
  publishing. Resolve rejection or divergence under repository policy; destructive
  history changes need explicit authorization.

Use `git push` for a correctly configured upstream, or an explicit remote and
branch for a new branch. Normal push authorization does not authorize force
pushing. When a force push is explicitly authorized, verify the target and use
`--force-with-lease`.

Report the push result. Check applicable CI or PR status within the requested
scope and use the environment's monitoring tools when waiting is requested.
A successful push alone does not establish that tests or deployment succeeded.
