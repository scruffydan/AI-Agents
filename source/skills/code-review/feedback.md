# Evaluate a Proposed Fix

Use this checklist when assessing supplied feedback under `code-review`.

- Is the suggestion technically correct for this codebase and targeted platform
  versions?
- Would it break existing behavior or a compatibility requirement?
- Why does the current implementation exist, and do its callers still need it?
- Does the suggestion address an actual use case or add unused infrastructure?
- Does the reviewer have the relevant context and established user decisions?

## When to push back

Push back when evidence shows a suggestion is technically incorrect, breaks
required behavior, adds unnecessary infrastructure, or conflicts with established
architecture or compatibility decisions. Identify missing context rather than
assuming the reviewer has it.

Use technical reasoning, reference relevant code and tests, and ask specific
questions when needed. Involve the user when an unresolved architectural choice
materially changes the outcome.

## Examples

**Compatibility:**

Reviewer: "Remove the legacy code."

Response: "The project supports macOS 10.15, but the replacement API requires
macOS 13. Keep the compatibility path unless the supported versions change."

**Unnecessary infrastructure:**

Reviewer: "Add metrics storage, date filters, and CSV export."

Response: "I found no callers for this endpoint in the repository. Is there an
external consumer or a reporting requirement? Without that use case, the added
storage and export infrastructure would be unnecessary."
