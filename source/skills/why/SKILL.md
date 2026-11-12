---
name: why
description: Investigate why code or an architectural decision exists using implementation, targeted history, and decision records. Use for design rationale questions rather than debugging failures or Five Whys process analysis.
---

# Investigate Design Rationale

Explain the evidence behind a specific design choice. Keep the investigation
report-only unless changes are separately authorized; a rationale question does
not authorize edits, instrumentation, commits, or external messages and writes.

## Bound the question

Identify the decision, files or symbols, and relevant version or time period.
Distinguish “why was this introduced?” from “what requires it now?” Reuse context
and narrow an ambiguous question only when the answer would materially change
the investigation. Match effort to the question; do not start a repository-wide
or all-category parallel sweep by default.

## Trace the decision

- Read the relevant implementation, callers, tests, and configuration to establish
  what the code does and which constraints are observable today. Current behavior
  alone cannot establish original intent.
- Use targeted history and blame to locate candidate changes, then read their
  diffs, messages, and surrounding code at the time. For example, use
  `git log --follow -- path`, `git blame -L start,end -- path`, or
  `git log -S 'symbol' -- path` as appropriate. The last touching commit may be
  formatting or a move; follow renames and earlier substantive changes when needed.
  Blame locates changes, not personal responsibility or proof of motive.
- Follow relevant design records, comments, issues, and available authorized PR
  descriptions and review discussions. Check dates and whether a proposal was
  adopted, rejected, or superseded. A PR association or an unmerged suggestion
  does not establish the rationale for the shipped code.
- Pursue only leads that bear on the question. Compare plausible alternatives
  against the evidence, including contradictions and later changes. Separate a
  historical constraint from one that still applies; avoid judging an old choice
  solely with present-day requirements.

Use only available, permitted sources. Do not assume a hosting integration or
private history is accessible, bypass a denied read, or publish private code in
search queries. If history is shallow, records are missing, or PR evidence is
unavailable, state the limit and continue with what can be established. Stop when
the question is adequately answered or the remaining gap needs unavailable
evidence; an unsuccessful search is not proof that no rationale existed.

## Separate evidence from explanation

Keep these distinctions visible in the answer:

- **Documented intent:** a contemporary source explicitly states the reason.
  Attribute it and check that it concerns the implemented decision.
- **Observed constraints:** code, tests, contracts, or records demonstrate a
  requirement or behavior. Explain what this supports without assigning intent.
- **Inference:** an explanation fits indirect evidence but was not stated.
  Label it, mention credible alternatives, and avoid presenting it as an author's
  motivation. Several consistent clues can strengthen an inference without
  turning it into documented intent.

Conflicting sources reduce confidence. Prefer an honest “not established” to a
confident story assembled from current code alone.

## Report proportionately

Lead with the answer and its evidence status. Give concrete references beside
material claims: file and line at a named revision, commit SHA and relevant diff,
or a direct link to a decision record or PR comment. Distinguish historical
references from current checkout locations.

State confidence and why, unresolved questions, and material search/access gaps.
Separate established reasons from possible trade-offs. If the question informs a
proposed change, identify constraints to preserve and the evidence that would
justify revisiting them; recommendations remain separate from implementation.
A short answer with a few strong references is enough for a narrow question.

## Source

Adapted from selected investigation and evidence practices in
[pstack's why skill](https://github.com/cursor/plugins/blob/ce649c03ac3b75b6ae80cbd15b7e2c536caedb5a/pstack/skills/why/SKILL.md)
and its
[epistemics reference](https://github.com/cursor/plugins/blob/ce649c03ac3b75b6ae80cbd15b7e2c536caedb5a/pstack/skills/why/references/epistemics.md).
The upstream orchestration and tool-specific workflow are not required here.
See [LICENSE](LICENSE) for the upstream MIT notice.
