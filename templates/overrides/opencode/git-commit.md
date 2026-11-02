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
    resource: "git log *"
    effect: allow
  - action: shell
    resource: "git diff *"
    effect: allow
  - action: shell
    resource: "git status *"
    effect: allow
  - action: shell
    resource: "git show *"
    effect: allow
  - action: shell
    resource: "git -C * log *"
    effect: allow
  - action: shell
    resource: "git -C * diff *"
    effect: allow
  - action: shell
    resource: "git -C * status *"
    effect: allow
  - action: shell
    resource: "git -C * show *"
    effect: allow
  - action: shell
    resource: "git * push *"
    effect: ask
  - action: question
    resource: "*"
    effect: deny
---

{{agent:body}}
