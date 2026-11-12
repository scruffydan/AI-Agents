---
name: unslop
description: Edit substantial agent prose or user-provided drafts for clarity, concrete evidence, and concision while preserving meaning, tone, and supported uncertainty.
---

# Unslop

Improve the requested prose without changing its argument, intended tone, audience,
or level of certainty. Respect the task's read-only and write boundaries: an edit
request does not authorize publishing, sending, or changing unrelated files.

## Edit for substance and clarity

- Make the answer or outcome easy to find while respecting the requested format
  and summary placement. Keep the detail the reader needs to understand, assess,
  or act on it; do not shorten for its own sake.
- Cut filler introductions, canned praise, generic conclusions, and claims of
  importance that add no information. Replace broad claims such as “improves
  efficiency” with the supported mechanism or result. If none is available, remove
  the claim or flag the evidence gap rather than inventing specifics.
- Replace vague attribution such as “experts say” with an available named source
  and the claim it supports. Remove unsupported authority claims; retain relevant
  observations as observations, clearly scoped to the evidence.
- Preserve caveats, limitations, citations, and distinctions between facts,
  inferences, and hypotheses. Remove empty hedging without turning a possibility
  into a fact or making a claim broader than its evidence.
- Use familiar, concrete words and name actors and actions when known. Explain
  necessary jargon for the audience; keep technical terms that carry precise
  meaning. Do not invent an actor to force active voice.
- Split dense sentences where separate ideas need room. Keep conditions,
  exceptions, and causal links attached to the claims they qualify. Use paragraphs
  or lists according to the material, without forcing a fixed number of points.
- Remove repeated ideas and strings of near-synonyms. Use the same term for the
  same concept unless a distinction matters. Preserve deliberate repetition that
  supports emphasis, voice, or comprehension.

Punctuation, adverbs, and technical vocabulary are choices to judge in context,
not categories to ban. Preserve quotations and literal identifiers; edit the
surrounding explanation when their exact form matters.

## Short self-edit pass

Reread the revision once. Check that each claim still has the same support and
certainty, each paragraph adds information, and the wording sounds natural for
this author and audience. Restore any meaning lost while cutting. This pass does
not need additional agents or tools. Return the edited prose in the requested
format, with a brief note about unresolved factual gaps only when useful.

## Source

Adapted from selected ideas in Lauren Tan's pstack
[unslop skill](https://github.com/cursor/plugins/blob/837067b75aa20ab58d7b2a2f6c0531e37118c596/pstack/skills/unslop/SKILL.md),
revision `837067b75aa20ab58d7b2a2f6c0531e37118c596`. The upstream MIT notice is
retained in [LICENSE](LICENSE). This adaptation uses portable metadata and a
single self-edit pass rather than upstream invocation settings or blanket style bans.
