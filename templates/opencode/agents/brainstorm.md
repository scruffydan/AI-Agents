---
description: Creative brainstorming mode for generating diverse ideas and exploring unconventional solutions.
mode: primary
model: {{model:brainstorm}}
permissions:
  - action: edit
    resource: "*"
    effect: deny
  - action: shell
    resource: "*"
    effect: deny
---

{{prompt:brainstorm}}
