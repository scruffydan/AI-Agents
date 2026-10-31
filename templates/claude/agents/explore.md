---
name: explore
description: Explore and answer questions about the codebase. Use this agent to find files, search code, understand implementations, and trace dependencies without consuming main conversation context.
tools: Glob, Grep, Read, List
model: {{model:mini_reasoning}}
---

{{prompt:explore}}
