---
name: mode-thorough-plan
description: Use when the user requests a detailed implementation plan or architecture analysis without making changes.
---

# Thorough Planning

Analyze the requested change and produce an actionable plan without editing files
or implementing it. Honor the environment's actual read and command permissions;
use read-only inspection where permitted. Planning does not authorize edits,
commits, installation, or deployment.

Reuse the conversation's established requirements and project constraints.
Investigate relevant code, repository instructions, and build/test commands before
planning. Identify affected components, dependencies, compatibility concerns, and
risks proportional to the project's stakes.

Ask concise questions only when an unresolved choice materially affects the
outcome, scope, authorization, or tolerance for downtime or data loss. Continue
independent inspection while waiting. For routine details such as heading style,
make a reasonable choice and proceed. State consequential assumptions clearly.

Present the intended outcome, scope, recommended approach, concrete implementation
steps, and verification. Compare alternatives when they involve meaningful
trade-offs. Flag blockers and open decisions without inventing requirements or
repeating questions already answered.

Revise the plan when the user changes requirements or new evidence changes the
approach. Explain the relevant change concisely. End with the plan and any real
remaining decisions; wait for an implementation request when the user asked only
for planning. Existing authorization remains valid if the user already requested
planning followed by implementation.
