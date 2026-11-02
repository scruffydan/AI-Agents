---
description: {{agent:description}}
mode: subagent
model: {{agent:model}}
permissions:
  - action: "*"
    resource: "*"
    effect: deny
  - action: websearch
    resource: "*"
    effect: allow
  - action: webfetch
    resource: "*"
    effect: allow
  - action: execute
    resource: "*"
    effect: allow
---

{{agent:body}}
