---
name: file-pr
description: Open, reuse, or update a GitHub pull request. Use when asked to file a PR or update an existing PR, including its title or description. Skip plain pushes and PR reviews.
---

# File PR

Open or update a PR only within the current task's authorization.

## Find the PR

Identify the head and base repositories and branches. Look for an open PR with
that exact head and base. If the same head has an open PR against a different
base, flag the mismatch and ask how to proceed before retargeting it or opening
another PR.

Review the intended diff against the actual base and apply the PR guidance in
`verification-before-completion`. Use `git-push` to publish branch changes when
the task calls for them.

## Reuse or update an existing PR

Reuse a matching open PR. Report its URL and make only the requested changes.
A request to update the branch does not by itself authorize editing the PR title
or description. If branch changes make the description inaccurate or incomplete,
explain what needs to change and ask before editing it, unless the user already
explicitly requested that description update. Continue authorized branch work
while awaiting that decision.

## Open a new PR or write authorized metadata

Create a PR when no matching one exists and creation is authorized. Use the
following writing guidance for new PRs and for authorized metadata edits.

PR titles usually become commit messages, so follow the repository's title
conventions. Look at recently merged PRs and Git history for examples. Prefer a
concise, human-readable title that explains why the change matters:

BAD

> ❌ perf(server): negotiate permessage-deflate on the websocket

GOOD

> ✅ perf(server): cut websocket frame size by 70%+ with gzipping

Open the description with a simple explanation of the problem based on the
user's original prompt, then briefly explain the solution. Do not lead with an
implementation inventory:

BAD

> ❌ Removed implicit workspace carry-over from every "new thread" entry point (cmd+n / cmd+shift+o, sidebar v1/v2 buttons, command palette). New threads inherit only the project from context; branch, worktree, and env mode always come from the configured defaults. Deleted buildContextualThreadOptions, startNewThreadInProjectFromContext, and the v1 sidebar's seed-context machinery.

GOOD

> ✅ My "new worktree" default was ignored when starting new threads on existing worktrees. Super unintuitive. Now your preferences always apply.

End the description with the attribution line that the user's or harness's
instructions specify. If none is specified, end with the public model name and
harness that made the changes, for example `Created with <model> in <harness>.`
Include subagent models that wrote part of the change. Use the model name the
harness reports. If model identity is unavailable, name the harness without
guessing a model.

Before submission, check the title, description, quotes, and attachments for
secrets and private details.

For a new PR, open it as ready for review unless the user asked for a draft.
If `gh pr create` fails because the GraphQL rate limit is used up, open it
through REST with
`gh api repos/<owner>/<repo>/pulls -f title=... -f head=... -f base=... -F body=@<file>`.

## Report

Confirm the PR URL and state. Say whether you opened, updated, or reused it and
identify any pending decision about its description. If the user asked to
monitor the PR, use the environment's PR monitoring tools.

Do not post a follow-up PR comment unless it serves the user's request. When a
comment is needed, use the `leaving-pr-comments` skill.

## Source

Adapted from Theo Browne's
[tstack file-pr skill](https://github.com/t3dotgg/tstack/blob/6efae364201abc9d9f07443e9caa461f42e51090/skills/file-pr/SKILL.md).
This adaptation retains the title and description examples and adds explicit
routes for new and existing PRs. The upstream MIT notice is retained in
[LICENSE](LICENSE).
