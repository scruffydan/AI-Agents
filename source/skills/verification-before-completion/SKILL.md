---
name: verification-before-completion
description: Use before claiming work is complete, fixed, or passing, or before committing or creating a PR, when verification evidence must support the result.
---

# Verification Before Completion

Support completion claims with observed evidence. Identify the checks relevant to
the requested change, run them, read the complete result, and report the outcome.
A changed file or an agent's success report does not prove correct behavior.

## Select and reuse evidence

Use repository instructions and the actual change to choose tests, lint, builds,
or manual checks. Scale verification to the impact; do not add tests that merely
restate documentation or mirror implementation. For a meaningful bug fix, verify
that a regression check fails for the original defect and passes with the fix.

Reuse a successful check from this session when its code, dependencies,
configuration, fixtures, and relevant environment remain unchanged. Moving from
implementation to commit or push does not itself invalidate evidence. Rerun
checks when relevant inputs change, a failure needs investigation, or a material
concern remains unresolved. Do not claim an old result verifies new changes.

## Report accurately

Inspect the final diff and confirm the requested behavior and scope. For delegated
work, review the resulting artifacts and verification evidence yourself.

State which checks actually ran and their outcomes, including failures and blocked
checks. Distinguish static inspection, automated tests, and live testing. A passing
linter does not prove a build passes; a passing build does not prove a bug is fixed.
If a check cannot run, explain the limitation without implying success.

Use `update-readme` for documentation accuracy. Verification, documentation, and
Git skills can share valid evidence rather than repeating the same checks.
