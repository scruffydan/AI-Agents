---
description: Analyze requirements and code to create an implementation plan without modifying files.
mode: primary
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
  - action: skill
    resource: "mode-thorough-plan"
    effect: allow
---

Load the `mode-thorough-plan` skill and follow its planning instructions.
