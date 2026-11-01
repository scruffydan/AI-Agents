---
name: brainstorm-with-agent
description: Use when the user requests brainstorming with the configured brainstorming model or agent, without editing files.
---

Use the `brainstorm` custom agent to explore the user's request with the configured
brainstorming model. Pass the request and relevant conversation context,
constraints, and decisions to the agent so it can work independently. Return its
ideas to the user and incorporate any follow-up feedback.

The agent owns the brainstorming instructions and model selection. Do not edit
files as part of this mode.
