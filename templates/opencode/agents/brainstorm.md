---
description: Creative brainstorming mode for generating diverse ideas and exploring unconventional solutions.
mode: primary
model: {{model:brainstorm}}#medium
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
---

{{prompt:brainstorm}}
