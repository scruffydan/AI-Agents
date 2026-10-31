# Validate at meaningful boundaries

After locating the root cause, decide where invalid state should be rejected.
Avoid spreading checks indiscriminately across callers.

- At an external input boundary, validate the contract and return an actionable
  error before starting work.
- In the domain operation that owns an invariant, enforce that invariant even
  when a different caller bypasses the external boundary.
- Around an irreversible side effect, verify the preconditions that make that
  operation safe and correct.

Each check should own a different failure mode. Keep one source of truth for
validation rules rather than copying predicates. Test the originating bug and
any distinct boundary whose behavior changed; confirm valid inputs still work.
