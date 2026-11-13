---
name: takeover
description: Finish someone else's pull request, branch, or agent thread while preserving the original contributors' credit. Use when the user asks to take over existing work or requests a takeover.
---

# Takeover

Take responsibility for finishing the original goal while preserving the
original contributors' credit. Do not defend an implementation just because
another agent already built it.

Read the source PR, branch, or thread, including review findings and the user's
later corrections. Resolve the handoff to the actual code and current head,
and account for uncommitted work. Treat the handoff as context, not proof.

For a replacement PR, import the original commits onto a new branch and add
your fixes separately. Honor an explicitly requested in-place or stacked
continuation instead. Do not overwrite unrelated work or change the original
PR without authorization.

Preserve Git authorship and existing co-author trailers. Credit the original
contributors in the PR description and link the original PR when there is one.
If the work will be squashed, preserve human author/co-author credit in the
merge commit too, using verified identities rather than guessed emails. Model
attribution is not a substitute for contributor credit.

Use `modernize` to update the continuation against its intended base and
current architecture. Rework what is necessary to finish the same goal, not
unrelated features. Simplify the implementation without dropping intended
behavior or surfaces. Recheck the source PR too: it may have improved while
you were working.

Independently verify the original failure and realistic workflows, following
repository guidance and permissions. Green mocked tests do not prove the user
experience works. State what remains unverified.

When the requested finish includes a PR, use `file-pr` to file or update it,
then check its CI and review status rather than stopping at creation. When the
user asked you to monitor it, wait with the environment's PR monitoring tools.
Use `leaving-pr-comments` for replies. Merge or close the original PR only when
authorized.

Report what you inherited, what you changed, how you verified it, how credit
was preserved, and any remaining decision.

## Source

Adapted from Theo Browne's
[tstack takeover skill](https://github.com/t3dotgg/tstack/blob/6efae364201abc9d9f07443e9caa461f42e51090/skills/takeover/SKILL.md).
The instruction body is unchanged except that the upstream `babysit-pr` handoff
now checks CI and review status and uses the environment's monitoring tools
when asked. The description was rewritten to name the credit requirement, and
this source note was added. The upstream MIT notice is retained in
[LICENSE](LICENSE).
