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
