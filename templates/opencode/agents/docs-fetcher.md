---
description: Fetch and extract relevant documentation from URLs. Use this agent when you need specific information from external documentation without flooding the main context with entire pages.
mode: subagent
model: {{model:mini_reasoning}}#high
permissions:
  - action: edit
    resource: "*"
    effect: deny
  - action: shell
    resource: "*"
    effect: deny
  - action: subagent
    resource: "*"
    effect: deny
  - action: question
    resource: "*"
    effect: deny
---

{{prompt:docs-fetcher}}
