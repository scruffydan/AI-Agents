# Write to shared knowledge

Read this before contributing to a configured shared knowledge store, or when a
change lands on a project's default branch while a shared wiki is configured.
The authorization, secrecy, and audience rules in [SKILL.md](SKILL.md) still apply.

For an authorized contribution to shared knowledge, follow that store's capture
workflow. Record source, date, scope, and confidence or decision status. Preserve
explicit corrections and mark superseded guidance so later retrieval finds the
current decision. Inferred preferences remain uncertain until confirmed.

When a change lands on a project's default branch, check whether it changes a fact
summarized in the configured shared wiki. For a material change, use the wiki's
authorized inbox workflow to record the affected page, what changed, and a link
to the landed revision. Check existing captures to avoid duplicates. An open PR
is still a proposal. Routine changes that leave the summary accurate need no capture.

Separate new capture notes from curation of maintained wiki pages. Reuse existing
capture templates and unique filenames; respect the store's concurrency policy.
During authorized curation, preserve captured sources, link synthesis to them,
update affected pages and the index, and log significant changes. Check for broken
links, unsupported summaries, and stale or conflicting claims.

Preserve both contributions if writers conflict, and report unsynchronized work.
Git publishing follows existing authorization and the Git workflow; never discard
notes or force-push to make synchronization succeed.
