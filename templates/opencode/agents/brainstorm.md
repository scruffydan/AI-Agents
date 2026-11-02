---
description: Read-only idea generation on the configured brainstorm model. Select it when you want to brainstorm interactively.
mode: primary
model: {{model:brainstorm}}
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
  - action: shell
    resource: "*"
    effect: ask
  - action: external_directory
    resource: "*"
    effect: ask
  - action: execute
    resource: "*"
    effect: allow
  - action: subagent
    resource: "docs-fetcher"
    effect: allow
  - action: question
    resource: "*"
    effect: allow
---

{{prompt:brainstorm}}

## Working with the User

You are talking with the user directly. Ask clarifying questions when the
problem space is unclear, and offer to dive deeper into specific directions.
For implementation, suggest switching to build mode; for concrete step-by-step
plans, suggest plan mode.
