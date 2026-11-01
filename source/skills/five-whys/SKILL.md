---
name: five-whys
description:
  Conduct root cause analysis using the Five Whys technique. Use when
  investigating problems, debugging issues, understanding failures, analyzing
  churn, or finding the underlying cause of any issue.
---

# Find a Cause with Five Whys

Start with a specific observed problem and its impact. Ask what caused it, then
what caused that condition. Support each link with evidence; label uncertainty
and investigate missing facts instead of inventing a chain.

Five questions is a guide, not a quota. Stop at a supported, actionable cause;
continue or branch when the evidence shows multiple contributing paths. Focus on
conditions and processes rather than assigning personal blame. Ask the user only
for information that cannot be established from available evidence.

For example, a request fails because a query times out; the query became slow
after an index was dropped; the migration omitted recreating it. Check the query
plan and migration before recommending a fix. Do not assume the explanation from
the example applies to the current failure.

Report the problem, causal chain, evidence and gaps, and the smallest practical
change that would prevent recurrence. Explain how to verify that change. Use
`systematic-debugging` for a software investigation and
`verification-before-completion` before claiming a fix worked.
