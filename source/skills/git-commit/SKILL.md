---
name: git-commit
description: Prepare commit messages and create authorized commits using repository conventions. Use when preparing a commit or drafting its message; the current conversation owns the workflow and the configured drafting agent handles history analysis.
---

# Git Commit

The parent owns the commit workflow in the current conversation. Follow the
user's and repository's authorization, preserve unrelated changes and untracked
files, and keep each commit focused. A message-only request does not authorize
staging or committing. Loading this skill only for message conventions does not
request a new commit.

## Prepare the changes

- Inspect the working tree and intended diff. For an authorized commit, stage
  only the intended changes and inspect `git diff --cached`. Do not silently
  include or unstage unrelated staged changes; resolve conflicting scope first.
- Use `verification-before-completion` for relevant checks and `update-readme`
  for README and existing AGENTS.md accuracy. Reuse valid session evidence.
- For a message-only request, leave the index untouched and identify the diff or
  changes the message should describe.

## Route message drafting

Automatically use the configured `git-commit` drafting agent when available and
delegation is permitted. Use its configured model profile so history analysis
runs on the cheaper drafting model and older messages stay out of the parent's
context. A separate user request to check conventions is unnecessary.

Give the child the repository location, intended scope, and any conventions
already established in the session. Let it inspect history itself; do not load
older messages into the parent first. Request the proposed message, reviewed
files, a brief summary of changes and conventions, and concerns, without raw Git
logs.

If delegation is unavailable or prohibited, report that limitation. The parent
may draft using reliable conventions already in context. Otherwise, ask how to
proceed before loading history into the parent or substituting another model.

## Message analysis and drafting

When acting as the drafting child, use only this section. Do not delegate again,
edit or stage files, run verification commands, commit, push, or ask the user for
approval. Report missing context or tools to the parent.

Read applicable repository instructions and inspect the staged diff, or the
parent-specified scope for a message-only request. If neither is available,
report the missing scope instead of staging changes or inventing a message.

Reuse established conventions when reliable. Otherwise inspect recent history:

```sh
git log -10 --oneline --no-decorate
```

Read full messages only when body or footer conventions need clarification:

```sh
git log -10 --format="%h %s%n%b%n"
```

Follow repository instructions and match its conventions: conventional commits,
free-form subjects, or custom formats. Match relevant prefixes, scopes,
capitalization, subject length, body style, and issue references. Do not impose
conventional prefixes on a repository that uses free-form messages. With little
or no history, follow explicit guidance or propose a concise descriptive subject
and mention the limited evidence.

Describe the actual change and its purpose. Include a body or footer when useful
or required by the repository, and do not invent issue references or claims.
Return the proposal and concise supporting findings to the parent; keep raw
history in the child's context.

## Validate and commit

The parent checks the proposal against the final staged diff for accuracy,
unintended edits, and sensitive data. If the intended changes have changed since
drafting, update the proposal or request a new draft. Commit only within existing
authorization, then report the hash and verification results.

Do not add an approval step when the commit is already authorized. Amend or
rewrite history only within authorization. Pushing requires separate permission;
use `git-push` when a push is requested.
