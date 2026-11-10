---
name: verification-before-completion
description: Choose proportionate verification and report evidence accurately for implementation, commits, pushes, PRs, and completion claims.
---

# Verification Before Completion

Match verification to the change, its risk, and the claim being made. Follow
explicit user and repository requirements. Completion does not automatically
require running tests, lint, or a build; inspection may be sufficient for a small
documentation or other low-impact edit.

## Match the workflow stage

- During implementation, use focused checks when they help establish behavior.
  For a meaningful bug fix, prefer a regression check that demonstrates the
  original defect and passes with the fix. Avoid tests that merely restate documentation
  or mirror implementation.
- Before a local commit, inspect the intended and staged diff for scope,
  unintended edits, sensitive data, and whitespace issues. Run additional checks
  only when the change warrants them or explicit requirements call for them.
  A commit is not a full-suite, lint, or build gate.
- Before a push, inspect the outgoing changes and reuse valid verification
  evidence. A push alone does not require another test run.
- At PR readiness, validate the accumulated branch changes with the broader
  relevant tests, lint, and builds, using local checks or equivalent CI results
  for the current revision. Run the full suite when warranted by the change or
  required by the repository. Report pending CI as pending.

## Select and reuse evidence

Choose the smallest useful check that supports the claim. If inspection is enough,
report what was reviewed. When running a command, read its complete result before
claiming it passed. A changed file or an agent's success report alone does not
prove correct behavior.

Reuse a successful check from this session when its code, dependencies,
configuration, fixtures, and relevant environment remain unchanged. Moving from
implementation to commit, push, or PR preparation does not itself invalidate
evidence. Rerun checks when relevant inputs change, a failure needs investigation,
or a material concern remains unresolved.

## Report accurately

Inspect the final diff and confirm the requested behavior and scope. For delegated
work, review the resulting artifacts and verification evidence yourself.

State which checks actually ran and their outcomes, including failures and blocked
checks. When tests were unnecessary, a brief explanation is enough. Distinguish
static inspection, automated tests, and live testing. A passing linter does not
prove a build passes; a passing build does not prove a bug is fixed. If a needed
check cannot run, explain the limitation without implying success.

When a feature spec or task record exists, compare the final behavior with its
acceptance criteria. Identify requirements without evidence, unexplained work,
and stale or contradictory decisions. Within authorized documentation work,
record actual results and remaining gaps in the existing record. Task completion
alone does not demonstrate that an acceptance criterion passed.
