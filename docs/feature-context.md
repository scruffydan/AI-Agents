# Durable Feature Context

The shared skills borrow a few useful practices from specification-driven
development while keeping documentation proportional to each project. This is
guidance and an optional template, not an installed Spec Kit dependency.

## Recommendations and sources

Primary sources consulted on 2026-11-10:

- [Spec Kit specification template](https://github.com/github/spec-kit/blob/main/templates/spec-template.md)
  describes observable acceptance scenarios. The optional feature record uses
  acceptance criteria to make intended behavior verifiable.
- [Spec Kit task template](https://github.com/github/spec-kit/blob/main/templates/tasks-template.md)
  organizes tasks around user stories and describes when tests are requested.
  Our record links requirements, tasks, and completion evidence; it does not
  require a new test for every task.
- [Anthropic's context engineering guidance](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents)
  describes structured notes outside the context window and retrieving relevant
  context as needed. Our recommendation is a compact resume section with links,
  progress, unresolved questions, and verification evidence.
- [Michael Nygard's architecture decision records](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
  capture context, decisions, status, and consequences, retaining superseded
  records. Apply that pattern to consequential choices; a separate ADR for every
  implementation detail would add unnecessary maintenance.

These are living references rather than pinned dependencies. The combined
template, traceability table, provenance labels, and proportional adoption are
design choices for this repository, not requirements imposed by these sources.

## Boundaries

Keep reusable agent behavior in these shared skills. Keep project requirements,
decisions, and progress in the target project's existing documentation so the
next harness can retrieve them. Link relevant records from the project's existing
instruction entry point when useful; keep that entry point concise.

Avoid duplicate specifications when a project already uses issues, ADRs, or Spec
Kit artifacts. Update the authoritative record and link to it. On resume, compare
recorded state with the actual checkout, and recheck important assumptions before
acting. Label imported research and unconfirmed claims separately from accepted
decisions, with source and date/version information where useful.

Saving context follows the task's existing write permissions. A request to plan
or review remains read-only. A saved handoff does not grant authorization for
pending actions. Exclude secrets and unnecessary transcripts; preserve relevant
evidence through concise summaries and links.
