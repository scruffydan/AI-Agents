# Wait for a condition in asynchronous tests

Use observable completion signals instead of guessing how long an operation
will take. Prefer awaiting a promise, event, or the test framework's built-in
condition helper over adding an arbitrary delay.

When polling is necessary, give it a deadline, a bounded interval, and a useful
timeout error that records the last observed state. The condition should inspect
state without repeating the operation being tested or causing side effects.

For a service readiness test, wait for a successful health response. For a UI
test, wait for the expected visible or enabled state. For queue processing,
observe the specific job's completion rather than waiting for the whole queue
to become empty.

Keep a fixed delay only when elapsed time itself is the behavior under test,
such as a debounce or timeout, and use the framework's fake clock when possible.
