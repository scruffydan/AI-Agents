---
description: Full code review orchestrating security, readability, performance, redundancy, and simplifier agents. Spawns all 5 specialist agents in parallel and synthesizes their findings.
model: {{model:deep_review}}
---

Use the `code-review` skill for a full review of the user's requested files or
changes, covering all five specialist perspectives. Return findings without
editing files unless the user also requests fixes.
