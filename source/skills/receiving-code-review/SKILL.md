---
name: receiving-code-review
description: Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor and verification, not performative agreement or blind implementation
---

# Evaluate Review Feedback

Read the feedback and verify each material claim against the actual code,
requirements, callers, and tests. A reviewer's confidence is not evidence.
Separate demonstrated defects from preferences and speculative improvements.

Explain technical disagreements with concrete evidence and a practical
alternative. Respect the user's informed decision and revisit it only when new
information matters. Acknowledge corrections plainly without performative
agreement or lengthy apologies.

Ask when unclear feedback would materially change the fix. Continue independent
work that does not depend on the answer. Do not let an ambiguous item block every
other item automatically.

When fixes are authorized, address correctness and security issues first. Make
focused changes and verify meaningful behavior changes with appropriate checks.
Avoid unrelated refactors or infrastructure the project does not need. Use
`verification-before-completion` and report what changed, what was checked, and
what remains unresolved. A request to review alone does not authorize fixes or
messages to external reviewers.

## Check the Proposed Fix

- Is it technically correct for this codebase and targeted platform versions?
- Would it break existing behavior or a compatibility requirement?
- Why does the current implementation exist, and do its callers still need it?
- Does the suggestion address an actual use case or add unused infrastructure?
- Does the reviewer have the relevant context and established user decisions?

## When To Push Back

Push back when:
- Suggestion breaks existing functionality
- Reviewer lacks full context
- Violates YAGNI (unused feature)
- Technically incorrect for this stack
- Legacy/compatibility reasons exist
- Conflicts with your human partner's architectural decisions

**How to push back:**
- Use technical reasoning, not defensiveness
- Ask specific questions
- Reference working tests/code
- Involve your human partner if architectural

## Examples

**Technical Verification (Good):**
```
Reviewer: "Remove legacy code"
✅ "Checking... build target is 10.15+, this API needs 13+. Need legacy for backward compat. Current impl has wrong bundle ID - fix it or drop pre-13 support?"
```

**YAGNI (Good):**
```
Reviewer: "Implement proper metrics tracking with database, date filters, CSV export"
✅ "Grepped codebase - nothing calls this endpoint. Remove it (YAGNI)? Or is there usage I'm missing?"
```
