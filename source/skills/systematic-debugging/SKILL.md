---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes
---

# Investigate Before Fixing

Establish the cause from evidence before changing behavior. Keep the investigation
proportional to the problem; a clear local failure does not need a formal incident
process.

1. Read the complete error and reproduce the failure with the smallest useful
   input. Note expected behavior, actual behavior, and conditions. For intermittent
   failures, compare passing and failing runs instead of guessing.
2. Inspect relevant recent changes, callers, configuration, and working examples.
   Trace the bad value or state back to where it first violates its contract.
   Use targeted diagnostics where needed; do not print secrets or broad environment
   dumps.
3. State a specific hypothesis and test it with the smallest relevant experiment.
   Change one cause at a time. If the evidence contradicts it, revise the hypothesis
   rather than stacking speculative fixes.
4. Fix the demonstrated cause. For meaningful behavior or security changes, add
   regression coverage that fails before the fix and passes afterward. Use existing
   checks or a focused manual reproduction where new tests would only restate a
   low-impact change.
5. Verify the original failure and related behavior with
   `verification-before-completion`. Remove temporary diagnostics and report the
   cause, fix, checks, and remaining uncertainty.

If repeated attempts fail, reassess assumptions and component boundaries. Ask for
help when missing information or access blocks progress; do not infer an
architectural failure solely from an arbitrary number of attempts.

Supporting techniques in this folder:

- `root-cause-tracing.md`: follow a failure backward through callers.
- `defense-in-depth.md`: validate at meaningful boundaries without duplicate rules.
- `condition-based-waiting.md`: wait for observable completion in asynchronous tests.
