---
description: Code redundancy and duplication specialist. Invoke for identifying duplicate code, repeated patterns, unused code, and opportunities for abstraction and DRY improvements.
mode: subagent
model: {{model:deep_review}}#medium
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

{{prompt:code-redundancy}}
