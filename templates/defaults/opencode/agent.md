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
    effect: deny
  - action: question
    resource: "*"
    effect: deny
---

{{agent:body}}
