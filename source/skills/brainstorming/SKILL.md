---
name: brainstorming
description: Use before implementation when a feature, behavior change, or architecture decision has unresolved requirements or meaningful design alternatives. Routine text edits and fully specified small changes do not need this workflow.
---

# Explore a Design Before Implementation

Understand the current code and the user's intended outcome. Reuse requirements,
constraints, and decisions already established in the conversation. Match the
amount of design work to the project's stakes and the change's complexity.

Ask focused questions only when missing information materially affects the design.
Continue independent investigation while waiting. For meaningful alternatives,
explain their trade-offs and recommend the simplest adequate approach.

Present the proposed behavior, affected components, data flow, and relevant error
handling and verification. Keep the explanation proportional to the change;
validate unresolved decisions without requiring approval after every section.
Honor authorization already given for implementation.

Record substantial agreed decisions in a design document when useful to the task
or required by the repository. Do not create documents, branches, or commits just
because brainstorming occurred. Use `implementation-workflow` for complex
implementation, reusing the design rather than restarting requirements analysis.

This skill guides design in the current conversation. Use `brainstorm-with-agent`
when the user requests the configured brainstorming model or agent.
