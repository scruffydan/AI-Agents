---
description: {{agent:description}}
mode: subagent
model: {{agent:model}}
permissions:
  - action: "*"
    resource: "*"
    effect: deny
  - action: read
    resource: "*"
    effect: allow
  - action: read
    resource: "*.env"
    effect: ask
  - action: read
    resource: "*.env.*"
    effect: ask
  - action: read
    resource: "*.env.example"
    effect: allow
  - action: glob
    resource: "*"
    effect: allow
  - action: grep
    resource: "*"
    effect: allow
  - action: external_directory
    resource: "*"
    effect: ask
  - action: execute
    resource: "*"
    effect: allow
  - action: shell
    resource: "*"
    effect: ask
  - action: shell
    resource: "git log"
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
---

{{agent:body}}
