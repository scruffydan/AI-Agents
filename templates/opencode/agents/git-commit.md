---
description: Generate conventional commit messages by analyzing git history and staged changes. Use when the user wants to commit changes, says "commit", or needs a commit message that follows repository conventions.
mode: subagent
model: {{model:git_commit}}#high
permissions:
  - action: edit
    resource: "*"
    effect: deny
  - action: shell
    resource: "*"
    effect: deny
  - action: shell
    resource: "git status"
    effect: allow
  - action: shell
    resource: "git status --short"
    effect: allow
  - action: shell
    resource: "git diff --no-ext-diff --no-textconv --cached"
    effect: allow
  - action: shell
    resource: "git log --oneline -10"
    effect: allow
  - action: subagent
    resource: "*"
    effect: deny
---

Use the permitted Git inspection commands above. For the staged diff, use
`git diff --no-ext-diff --no-textconv --cached`; never stage, commit, or push.

{{prompt:git-commit}}
