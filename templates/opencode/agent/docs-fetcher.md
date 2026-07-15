---
description: Fetch and extract relevant documentation from URLs. Use this agent when you need specific information from external documentation without flooding the main context with entire pages.
mode: subagent
model: {{model:mini_reasoning}}
reasoningEffort: high
permission:
  edit: deny
  bash: deny
  question: deny
---

{{prompt:docs-fetcher}}
