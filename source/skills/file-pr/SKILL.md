---
name: file-pr
description: Open a concise GitHub pull request whose title and description lead with the problem it solves. Use when the user asks to file, open, or create a PR; not for a plain push or for reviewing an existing PR.
---

# File PR

Filing a PR publishes the branch and its description. Do it only when the user
asked for a PR or the current task already authorizes one.

Before filing, check whether a PR for this branch already exists. Review the
diff locally against the base branch (usually `origin/main`) to make sure its
contents match the goal. Apply the PR guidance in
`verification-before-completion`, and use `git-push` to publish the branch.

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

Open a real PR rather than a draft so review bots run, unless the user asked
for a draft. If `gh pr create` fails because the GraphQL rate limit is used up,
open it through REST with
`gh api repos/<owner>/<repo>/pulls -f title=... -f head=... -f base=... -F body=@<file>`.
If the user also asked to monitor the PR, use the environment's PR monitoring
tools.

Do not post a follow-up PR comment unless it serves the user's request. When a
comment is needed, use the `leaving-pr-comments` skill.

## Source

Adapted from Theo Browne's
[tstack file-pr skill](https://github.com/t3dotgg/tstack/blob/6efae364201abc9d9f07443e9caa461f42e51090/skills/file-pr/SKILL.md).
The title and description guidance and examples are unchanged. This adaptation
adds the authorization sentence and hands verification and pushing to
`verification-before-completion` and `git-push`. It defers to an attribution
line set by user or harness instructions, allows a requested draft, and replaces
the upstream `babysit-pr` handoff with the environment's monitoring tools. The
description was rewritten to name what the skill covers and excludes, and this
source note was added. The upstream MIT notice is retained in [LICENSE](LICENSE).
