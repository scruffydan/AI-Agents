---
name: code-review
description: Review code or a diff, coordinate specialist reviewers, and evaluate supplied review feedback before applying it. Use when asked to review code or changes, run a targeted or full specialist review, or assess a reviewer's comments.
---

# Code Review and Feedback

## Shared evidence and authorization

Establish the intended behavior and project constraints. Validate material claims
against the actual code, requirements, callers, tests, and targeted platform
versions. A reviewer's confidence is not evidence. Separate demonstrated defects
from preferences and speculative improvements. Require profiling or other
evidence for numeric performance claims.

Keep reviews and feedback evaluation report-only unless fixes are authorized;
a severe finding alone does not authorize edits. A request to review or evaluate
feedback alone does not authorize messages to external reviewers. Respect the
user's scope, agent count, execution method, and read-only requirements. Keep
actions within actual permissions and reuse established authorization rather than
asking again for routine choices.

## Choose a route

- To review files or a diff, use **Review code** below.
- To assess supplied feedback or implement review suggestions, use **Evaluate
  supplied feedback** below. This route does not automatically launch specialists
  or a full review.
- For a request that includes both, evaluate the feedback and perform only the
  additional code review requested.

## Review code

Inspect the requested files or diff and relevant callers.

The parent reviewer owns integration and the final judgment: whether the change
meets its requirements and fits the components around it. In a targeted or
straightforward review, check correctness directly, including edge cases and
whether tests cover the change. In a full review, `code-correctness` gives an
independent read of that ground, which matters most when the parent wrote the
change. Verify its findings like any other specialist's, and combine them with
your own checks.

- For a targeted request, use only the relevant perspectives. An ordinary review
  does not automatically require four agents; inspect straightforward code directly.
- For an explicitly requested full review, cover all four specialists below.

Full-review specialists:

- `code-correctness`: logic, edge cases, failure paths, contracts, and test
  coverage.
- `code-security`: attack surface, trust boundaries, and data exposure.
- `code-performance`: algorithms, I/O, memory, and concurrency.
- `code-maintainability`: clarity, duplication and dead code, and complexity.

Optional targeted perspective:

- `code-blast-radius`: indirect impact beyond the diff, compatibility, and safety
  assumptions. Opt in when requested, especially for API or schema changes,
  shared libraries, and migrations. It is not added automatically to ordinary or
  full reviews. For example, request a blast-radius pass on a schema migration
  and its readers and writers.

The blast-radius specialist reports confirmed risks, investigated and cleared
cases, and unresolved assumptions, and recommends checks without running them.
The parent runs those checks, retains overall correctness, and deduplicates its
findings with the other perspectives.

Use the environment's supported agent tools and configured models. For a full
review, run specialists concurrently within available capacity; queue remaining
specialists when capacity is limited. If delegation is unavailable, perform those
passes directly and disclose that limitation. Never invent an agent or assume
that a permission configuration is enforced across harnesses.

Give each specialist the review scope as changed paths with line ranges or as
the diff text. Some harnesses give reviewers only file read and search tools, so
they cannot compute a diff or read history themselves. Add the requirements,
relevant context, and explicit read-only/report-only instructions. For a
blast-radius pass, also pass the relevant history. Do not let reviewers modify
files or ask the user questions; they should return uncertainties to the calling
agent. Keep commands within the review's authorized scope and the agent's actual
permissions.

Combine duplicate findings and discard unsupported claims. Prioritize concrete
correctness and security risks over cosmetic changes.

For each material finding, provide severity on the specialists' shared scale
(critical, high, medium, low), a file and line reference, the trigger and
impact, and a practical recommendation. Explain material conflicts
between supported recommendations. Identify uncertainties, checks performed, and
checks that were not run.
If no actionable issues are found, say so and state the review's limits.

## Evaluate supplied feedback

Read [feedback.md](feedback.md) for the proposed-fix checklist and examples. Verify
each material claim and proposed fix before deciding whether or how to apply it.
Report your assessment, evidence, and recommendation for each material item,
including remaining uncertainties.

Explain technical disagreements with concrete evidence and a practical
alternative. Respect the user's informed decision and revisit it only when new
information matters. Acknowledge corrections plainly without performative
agreement or lengthy apologies.

Ask when unclear feedback would materially change the fix. Continue independent
work that does not depend on the answer; an ambiguous item need not block every
other item. Do not expand feedback evaluation into a specialist or full review
unless the user requests that additional review.

## Authorized fixes

When fixes are authorized, address correctness and security issues first. Make
focused changes and verify meaningful behavior changes with appropriate checks.
Avoid unrelated refactors or infrastructure the project does not need. Resolve
routine choices within existing authorization; ask only about material unresolved
trade-offs. Use `verification-before-completion` and report what changed, what was
checked, and what remains unresolved. Review findings do not replace tests or CI.
