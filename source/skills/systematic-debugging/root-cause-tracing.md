# Trace a failure to its source

Use backward tracing when a failure is reported far from the operation that
introduced the bad state.

1. Capture the failing input, observed value, error, and call path.
2. Inspect the caller that supplied the value. Determine whether it received
   bad input or produced the bad value itself.
3. Repeat at each boundary until you find the first violated invariant.
4. If the path is unclear, add targeted temporary instrumentation at those
   boundaries. Record types, state transitions, or presence rather than secrets.
5. Reproduce the failure at the earliest faulty operation, correct its cause,
   and verify both that operation and the original failing path.

For intermittent failures, compare a passing and failing trace under the same
conditions before changing behavior. Remove temporary diagnostics after the
regression is covered.
