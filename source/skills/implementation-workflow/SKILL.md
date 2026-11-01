---
name: implementation-workflow
description: Use when implementing complex features, substantial refactors, or high-risk changes requiring coordinated architecture, testing, and delivery decisions.
---

# Implement a Complex Change

Scale the process to the project's users, lifespan, and tolerance for downtime or
data loss. Use existing architecture and dependencies where adequate. Routine
edits do not need a formal design or every step below.

1. Establish the intended behavior, acceptance criteria, constraints, and relevant
   callers. Reuse decisions already made. Use `brainstorming` for unresolved
   design choices or `mode-thorough-plan` for a planning-only request.
2. Choose the simplest adequate design. Identify affected interfaces, data changes,
   dependencies, and failure paths. Explain meaningful trade-offs before making
   a consequential choice; avoid speculative infrastructure or flexibility.
3. Implement in small, verifiable steps. Preserve unrelated work and compatibility
   constraints. Use `executing-plans` for a written plan and delegate only when
   authorized and useful.
4. Verify the changed behavior and relevant failure paths. Match security review
   and regression coverage to the actual risks. Use `code-review` when a review
   is requested or warranted; check findings against the code before fixing them.
5. Optimize only when requirements or measurements show a problem. Record material
   design decisions when useful, update documentation with `update-readme`, and
   use `verification-before-completion` for the final handoff.

Continue within existing authorization. Commits, external messages, publishing,
and deployment remain subject to the user's and repository's instructions.
