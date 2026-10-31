---
description: Answer general questions unrelated to the current coding session. Use this agent to handle tangential questions without consuming main conversation context.
mode: subagent
model: {{model:sidebar}}#medium
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

{{prompt:sidebar}}
