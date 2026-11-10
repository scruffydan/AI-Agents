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
- [Karpathy's LLM Wiki proposal](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
  describes preserved source material, a maintained linked wiki, index-first
  retrieval, and checks for stale or conflicting knowledge. The context skill
  follows an existing store's capture and curation workflow rather than imposing
  another layout. The proposal is an adaptable idea, not a product specification.

These are living references rather than pinned dependencies. The combined
template, traceability table, provenance labels, and proportional adoption are
design choices for this repository, not requirements imposed by these sources.

## Boundaries

The `project-context` skill supplies retrieval and handoff guidance across all
three harnesses. Shared base instructions call for it on substantial work or
resume. It uses an existing configured knowledge pointer; it does not provision a
wiki, install a search service, or establish a live integration. Agent-specific
memory can point to the common store without becoming a second authoritative copy.

Keep reusable agent behavior in these shared skills. Keep project requirements,
decisions, and progress in the target project's existing documentation so the
next harness can retrieve them. Link relevant records from the project's existing
instruction entry point when useful; keep that entry point concise.

Avoid duplicate specifications when a project already uses issues, ADRs, or Spec
Kit artifacts. For substantial authorized work that needs continuity, update an
existing issue, PR, or project record. When a local handoff file is needed, use a
single rolling `CONTEXT.md` at the project root or an existing equivalent. Keep
active goals, decisions, status, verification, and next actions concise, linking
to authoritative details. The detailed feature outline is optional for complex
work; avoid documents per feature or session and separate context archives.

Update the record at meaningful handoffs. At completion, cancellation, or
supersession, preserve lasting information in the relevant issue, PR, or existing
documentation before pruning obsolete progress. Keep unrelated active work and
unresolved risks. When nothing remains active, leave `No active work` and useful
pointers in the context file. These updates require writing authorization.

On resume, compare recorded state with the actual checkout, and recheck important
assumptions before acting. Label imported research and unconfirmed claims
separately from accepted decisions, with source and date/version information
where useful.

Saving context follows the task's existing write permissions. A request to plan
or review remains read-only. A saved handoff does not grant authorization for
pending actions. Exclude secrets and unnecessary transcripts; preserve relevant
evidence through concise summaries and links.

## Verification and rollout

Build and install as usual for the selected harnesses. The build copies the skill
and feature template unchanged; the installer does not configure a knowledge
location or publish captures. Keep local pointers in local instructions so a
reinstall of generated global instructions does not erase the only copy.

Test any configured wiki integration in a fresh session: retrieve a known scoped
fact, check that an explicit correction supersedes stale advice, and resume a
project from its own task record. If writes are enabled, confirm another session
can retrieve an authorized capture and that competing contributions are preserved.
Record which agent and integration were tested. Passing the repository's build
checks establishes artifact delivery, not reliable agent recall or live wiki sync.

Start with the existing index and text search. Add a search service only if
retrieval evidence shows a need, keeping Markdown authoritative and any index
rebuildable. Private wiki content and paths belong in an appropriate private
destination; publishing generic guidance does not authorize copying those details.
