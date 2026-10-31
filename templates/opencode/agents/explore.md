---
description: Explore and answer questions about the codebase. Use this agent to find files, search code, understand implementations, and trace dependencies without consuming main conversation context.
mode: subagent
model: {{model:mini_reasoning}}#high
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

{{prompt:explore}}
