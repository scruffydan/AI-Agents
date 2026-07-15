---
description: Simplifies and refines code for clarity, consistency, and maintainability while preserving all functionality. Focuses on recently modified code unless instructed otherwise.
mode: subagent
model: {{model:deep_review}}
reasoningEffort: medium
permission:
  edit: deny
  bash: deny
  question: deny
---

{{prompt:code-simplifier}}
