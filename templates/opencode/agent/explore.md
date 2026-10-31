---
description: Explore and answer questions about the codebase. Use this agent to find files, search code, understand implementations, and trace dependencies without consuming main conversation context.
mode: subagent
model: {{model:mini_reasoning}}
reasoningEffort: high
permission:
  edit: deny
  bash: deny
  question: deny
---

{{prompt:explore}}
