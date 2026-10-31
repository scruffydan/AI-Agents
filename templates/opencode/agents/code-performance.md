---
description: Performance optimization specialist. Invoke for identifying bottlenecks, optimizing algorithms, memory usage, I/O operations, and concurrency patterns.
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

{{prompt:code-performance}}
