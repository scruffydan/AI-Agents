---
name: code-review
description: Use when reviewing code or changes, requesting specialist findings, or evaluating supplied code review feedback before deciding whether or how to apply it.
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

The parent reviewer owns functional correctness, integration, and regression
coverage. Check the changed behavior against requirements and relevant callers,
including edge cases, component interactions, and whether tests cover the change.
Combine these checks with the specialist findings.

- For a targeted request, use only the relevant perspectives. An ordinary review
  does not automatically require five agents; inspect straightforward code directly.
- For an explicitly requested full review, cover all five specialists below.

Full-review specialists:

- `code-security`: attack surface, trust boundaries, and data exposure.
- `code-readability`: naming, documentation, and formatting.
- `code-performance`: algorithms, I/O, memory, and concurrency.
- `code-redundancy`: duplication and dead code.
- `code-simplifier`: control flow and complexity.

Optional targeted perspective:

- `code-blast-radius`: indirect impact beyond the diff, compatibility, and safety
  assumptions. Opt in when requested, especially for API or schema changes,
  shared libraries, and migrations. It is not added automatically to ordinary or
  full reviews. For example, request a blast-radius pass on a schema migration
  and its readers and writers.

The blast-radius specialist inspects authorized code, history, and records only;
it does not edit files, create tests or scripts, execute code or tests, publish,
or delegate. It distinguishes confirmed risks, investigated and cleared cases,
and unresolved assumptions, recommending the smallest useful checks to the
parent. The parent owns execution and implementation, retains overall
correctness, and deduplicates findings with the other perspectives.

Use the environment's supported agent tools and configured models. For a full
review, run specialists concurrently within available capacity; queue remaining
specialists when capacity is limited. If delegation is unavailable, perform those
passes directly and disclose that limitation. Never invent an agent or assume
that a permission configuration is enforced across harnesses.

Give each specialist the target, requirements, relevant context, and explicit
read-only/report-only instructions. Do not let reviewers modify files or ask the
user questions; they should return uncertainties to the calling agent. Keep
commands within the review's authorized scope and the agent's actual permissions.

Combine duplicate findings and discard unsupported claims. Prioritize concrete
correctness and security risks over cosmetic changes.

For each material finding, provide severity, a file and line reference, the
trigger and impact, and a practical recommendation. Explain material conflicts
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
