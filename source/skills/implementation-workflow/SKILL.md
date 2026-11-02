---
name: implementation-workflow
description: Use when implementing a complex feature, a substantial refactor, or a high-risk change that spans several components or touches security, data, or compatibility. Not needed for small, well-specified, or routine edits.
---

# Implementation Workflow

Scale each step to the project's stakes and reuse existing decisions and
dependencies. Use `brainstorming` for unresolved design choices and
`mode-thorough-plan` for an analysis-only request.

1. Clarify scope: the goal, acceptance criteria, and constraints. Ask only when
   missing information would change the outcome.
2. Identify the affected components, interfaces, and data, and the main risks,
   such as compatibility, data loss, and security.
3. Implement in small, verifiable increments, tackling the riskiest part first.
4. Test meaningful behavior, including error paths and edge cases, and run the
   project's existing checks.
5. For changes to authentication, authorization, input handling, secrets, or
   sensitive data, use the `code-security` agent when available.
6. Finish with `verification-before-completion` and `update-readme`. Commits,
   pushes, and deployment remain subject to user and repository instructions.
