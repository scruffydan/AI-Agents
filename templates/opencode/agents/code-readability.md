---
description: Code readability and maintainability specialist. Invoke for reviewing naming conventions, code structure, formatting, and documentation quality.
mode: subagent
model: {{model:deep_review}}
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

{{prompt:code-readability}}
