---
name: code-review
description: Use when reviewing code or changes, requesting specialist findings, or performing an explicit full code review before a major PR or release.
---

# Code Review

Review the requested files or diff and relevant callers. Establish the intended
behavior and project constraints before judging a change. Keep reviews report-only
unless the user also requests fixes; a severe finding alone does not authorize edits.

## Choose the scope

- For a targeted request, use only the relevant perspectives. An ordinary review
  does not automatically require five agents; inspect straightforward code directly.
- For an explicitly requested full review, cover all five specialists below.
- Respect a user-specified agent count, execution method, and read-only scope.

Available specialists:

- `code-security`: input handling, authentication, authorization, and data exposure.
- `code-readability`: naming, structure, documentation, and maintainability.
- `code-performance`: algorithms, queries, I/O, memory, and concurrency.
- `code-redundancy`: duplication, unused code, and shared business rules.
- `code-simplifier`: nesting, unnecessary complexity, and simpler control flow.

Use the environment's supported agent tools and configured models. For a full
review, run specialists concurrently within available capacity; queue remaining
specialists when capacity is limited. If delegation is unavailable, perform those
passes directly and disclose that limitation. Never invent an agent or assume
that a permission configuration is enforced across harnesses.

## Review and report

Give each specialist the target, requirements, relevant context, and explicit
read-only/report-only instructions. Do not let reviewers modify files or ask the
user questions; they should return uncertainties to the calling agent. Keep
commands within the review's authorized scope and the agent's actual permissions.

Validate findings against the code, combine duplicates, and discard unsupported
claims. Prioritize concrete correctness and security risks over cosmetic changes.
Require profiling or other evidence for numeric performance claims.

For each material finding, provide severity, a file and line reference, the
trigger and impact, and a practical recommendation. Explain actual conflicts
between recommendations without inventing debates or forcing every specialist to
comment. Identify uncertainties, checks performed, and checks that were not run.
If no actionable issues are found, say so and state the review's limits.

When fixes are requested, use `receiving-code-review` to evaluate feedback and
`verification-before-completion` to validate the resulting changes. Resolve
routine choices within existing authorization; ask only about material unresolved
trade-offs. Review findings do not replace tests or CI.
