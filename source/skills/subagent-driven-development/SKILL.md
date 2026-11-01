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

The following example illustrates separate specification and code-quality checks
for a substantial task with implementation and commits already authorized. Choose
the review depth for the actual task and respect requested checkpoints; the
example does not require two child reviews for every small edit.

## Example Workflow

```
You: I'm using Subagent-Driven Development to execute this plan.

[Read plan file once: docs/plans/feature-plan.md]
[Extract all 5 tasks with full text and context]
[Track all tasks with the environment's available planning tool]

Task 1: Hook installation script

[Get Task 1 text and context (already extracted)]
[Dispatch implementation subagent with full task text + context]

Implementer: "Before I begin - should the hook be installed at user or system level?"

You: "User level (~/.config/superpowers/hooks/)"

Implementer: "Got it. Implementing now..."
[Later] Implementer:
  - Implemented install-hook command
  - Added tests, 5/5 passing
  - Self-review: Found I missed --force flag, added it
  - Committed

[Dispatch spec compliance reviewer]
Spec reviewer: ✅ Spec compliant - all requirements met, nothing extra

[Get git SHAs, dispatch code quality reviewer]
Code reviewer: Strengths: Good test coverage, clean. Issues: None. Approved.

[Mark Task 1 complete]

Task 2: Recovery modes

[Get Task 2 text and context (already extracted)]
[Dispatch implementation subagent with full task text + context]

Implementer: [No questions, proceeds]
Implementer:
  - Added verify/repair modes
  - 8/8 tests passing
  - Self-review: All good
  - Committed

[Dispatch spec compliance reviewer]
Spec reviewer: ❌ Issues:
  - Missing: Progress reporting (spec says "report every 100 items")
  - Extra: Added --json flag (not requested)

[Implementer fixes issues]
Implementer: Removed --json flag, added progress reporting

[Spec reviewer reviews again]
Spec reviewer: ✅ Spec compliant now

[Dispatch code quality reviewer]
Code reviewer: Strengths: Solid. Issues (Important): Magic number (100)

[Implementer fixes]
Implementer: Extracted PROGRESS_INTERVAL constant

[Code reviewer reviews again]
Code reviewer: ✅ Approved

[Mark Task 2 complete]

...

[After all tasks]
[Perform a final code review appropriate to the change]
Final reviewer: All requirements met, ready to merge

Done!
```

Adapted from [obra/superpowers](https://github.com/obra/superpowers).
