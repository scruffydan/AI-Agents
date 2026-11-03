---
description: {{agent:description}}
mode: subagent
model: {{agent:model}}
permissions:
  - action: edit
    resource: "*"
    effect: deny
  - action: shell
    resource: "*"
    effect: ask
  - action: shell
    resource: "git log"
    effect: allow
  - action: shell
    resource: "git log -10 --format=full"
    effect: allow
  - action: shell
    resource: "git log -10 --oneline --no-decorate"
    effect: allow
  - action: shell
    resource: "git status"
    effect: allow
  - action: shell
    resource: "git status --short"
    effect: allow
  - action: shell
    resource: "git diff --no-ext-diff --no-textconv"
    effect: allow
  - action: shell
    resource: "git diff --no-ext-diff --no-textconv --cached"
    effect: allow
  - action: shell
    resource: "git diff --no-ext-diff --no-textconv --staged"
    effect: allow
  - action: shell
    resource: "git show --no-ext-diff --no-textconv HEAD --stat"
    effect: allow
  - action: question
    resource: "*"
    effect: deny
  - action: subagent
    resource: "*"
    effect: deny
---

{{agent:body}}
