---
description: Answer general questions unrelated to the current coding session. Use this agent to handle tangential questions without consuming main conversation context.
mode: subagent
model: {{model:sidebar}}
reasoningEffort: medium
permission:
  edit: deny
  bash: deny
  question: deny
---

{{prompt:sidebar}}
