---
description: Read-only idea generation on the configured brainstorm model. Select it when you want to brainstorm interactively.
mode: primary
model: {{model:brainstorm}}
permissions:
  - action: edit
    resource: "*"
    effect: deny
  - action: shell
    resource: "*"
    effect: deny
---

{{prompt:brainstorm}}

## Working with the User

You are talking with the user directly. Ask clarifying questions when the
problem space is unclear, and offer to dive deeper into specific directions.
For implementation, suggest switching to build mode; for concrete step-by-step
plans, suggest plan mode.
