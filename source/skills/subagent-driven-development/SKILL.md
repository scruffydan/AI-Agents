---
name: subagent-driven-development
description: Use when executing implementation plans with independent tasks in the current session
---

# Execute a Plan with Subagents

Use the environment's supported delegation tools and honor the user's requested
agent count, model, settings, and isolation. If delegation is unavailable or
prohibited, explain the limitation and do the authorized work directly.

Read the plan once and split it into tasks with clear acceptance criteria and
file ownership. Delegate independent work concurrently only when permitted;
sequence tasks that depend on each other or would edit the same files.

Give each child the task, relevant plan excerpt, repository context, allowed
files and actions, verification commands, and commit authorization. Tell workers
they share the codebase and must preserve others' changes. Explicitly preserve
read-only restrictions for research and review tasks. Children should perform
their task themselves unless their brief permits further delegation.

Use the local briefs where helpful:

- `implementer-prompt.md` for implementation.
- `spec-reviewer-prompt.md` for checking requirements and scope.
- `code-quality-reviewer-prompt.md` for correctness and maintainability review.

Answer child questions from established context; ask the user only when missing
information matters. Validate results against the actual artifacts and test
output. Check requirements before code quality; combine checks for small changes
and use separate reviewers when complexity or stakes warrant them. Fix routine
findings directly rather than starting another agent for every edit.

Recheck affected behavior after fixes and inspect the combined diff. Use
`verification-before-completion` and `update-readme` for handoff. Stop unneeded
children and report remaining blockers. Delegation does not expand authorization
for commits, external messages, pushing, or deployment.

Adapted from [obra/superpowers](https://github.com/obra/superpowers).
