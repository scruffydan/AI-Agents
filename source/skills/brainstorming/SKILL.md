---
name: brainstorming
description: Explore unresolved requirements or design alternatives before implementation, or use the configured brainstorming agent when explicitly requested. Routine text edits and fully specified small changes do not need this workflow.
---

# Explore a Design Before Implementation

Work in the current conversation by default. Use the configured-agent path below
only when the user explicitly requests the brainstorming model or agent.

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

## Configured Brainstorming Agent

In Codex and Claude Code, delegate to the `brainstorm` agent, which owns the
creative exploration instructions and model selection. Pass the user's request,
relevant conversation context, constraints, and established decisions so it can
work independently. Return its ideas to the user and incorporate follow-up feedback.

In OpenCode, use the `brainstorm` primary agent and select its configured model
in `/models`. An existing session keeps its selected model when changing agents;
loading this skill alone does not switch it.

Keep this path read-only in both the current conversation and the agent: do not
edit files or run shell commands. If the requested agent or model is unavailable,
report the limitation instead of silently substituting another model.
