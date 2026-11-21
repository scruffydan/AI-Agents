---
name: modernize
description: Rebase a pull request onto its current base, or assess whether an aging PR is still worth landing. Use for explicit PR rebases and requests to refresh or modernize an old PR.
---

# Modernize

For a plain rebase request, prepare the PR and go directly to **Rebase without
losing intent**. For a request to modernize or reassess the PR, also investigate
what changed on the base branch and choose a disposition before rebasing.

## Guardrails

- Treat existing worktree changes as user-owned. Rebase in an isolated checkout
  and leave the active worktree intact.
- A request to modernize or rebase a PR authorizes rebasing and updating that
  PR's branch. It does not authorize merging, closing, changing the base branch,
  or expanding scope. If the branch belongs to another contributor, confirm
  before rewriting it.
- Never use an unqualified force push. Update a rebased branch with
  `--force-with-lease` against the head SHA observed before the rebase.
- Do not post a PR comment unless the user asked for one. Use the
  `leaving-pr-comments` skill for every comment posted on the user's behalf.

## Prepare the PR

Resolve the PR and record its URL, state, base, head repository and branch,
current head SHA, author, checks, and review state. Fetch the exact head and base
branches from their respective repositories without pulling into local branches.
Record the fetched head SHA for the push lease. Inspect the PR diff to identify
the behavior the rebase must preserve.

## Reassess an aging PR

Read the title, body, linked issues, commits, review threads, and complete diff.
State the original goal. Find the merge base and inspect commits and diffs added
to the base branch since the PR diverged. Search merged and open PRs when titles,
code paths, or behavior suggest a replacement or competing implementation.

Look beyond overlapping lines:

- Has the same user-facing problem already been solved?
- Did APIs, types, schemas, dependencies, or architectural boundaries change?
- Do both sides now claim ownership of the same behavior or invariant?
- Was the code being changed deleted, moved, or intentionally simplified?
- Would landing the PR restore an old behavior or create two ways to do the
  same thing?
- Is the original benefit still large enough to justify the maintenance cost?

Do not describe a PR as current merely because Git reports no conflicts.

### Choose a disposition

Use one of these recommendations:

- **MODERNIZE**: the goal is still useful and the implementation remains the
  right shape. Rebase, resolve conflicts, test, and update the branch.
- **REWORK**: the goal is still useful, but a mechanical rebase would preserve
  the wrong implementation. Explain the smallest credible rewrite and stop
  before pushing unless the user also asked for that rework.
- **CLOSE**: the PR is superseded, obsolete, directionally wrong, or no longer
  worth its cost. Cite concrete evidence and stop. Do not spend time rebasing an
  obsolete branch, and do not close it without explicit permission.

Be willing to recommend `CLOSE`. Age alone is not evidence, and sunk effort is
not a reason to keep a PR alive.

## Rebase without losing intent

For a plain rebase request or a `MODERNIZE` disposition:

1. Create an isolated checkout at the recorded PR head.
2. Rebase its commits onto the freshly fetched base branch.
3. Resolve each conflict according to the PR's current intent and the base
   branch's newer invariants. If a conflict reveals a product or architecture
   disagreement, ask the user for the decision needed to continue a plain rebase.
   When modernizing, reconsider the disposition.
4. Compare the pre-rebase and post-rebase commit series with `git range-diff`
   and inspect the final diff. Confirm that no intentional behavior disappeared
   and no already-landed behavior was reintroduced.
5. Run the repository's focused checks for the touched area. Distinguish real
   failures from pre-existing or infrastructure failures.
6. Follow `git-push` to target only the PR's head branch, with an explicit lease
   tied to the recorded SHA. If the lease fails, fetch and reassess rather than
   overwriting new work.

Do not merge the PR.

## Report

For a plain rebase, report the PR URL, rebase and push result, checks, and any
unresolved conflicts. For modernization, lead with `MODERNIZE`, `REWORK`, or
`CLOSE` and the reason. Then summarize:

- meaningful changes on the base branch;
- conceptual conflicts or confirmation that none were found;
- the rebase and push result, if performed;
- checks run and their results;
- the remaining decision or work, with a link to the PR.

Separate observed facts from judgment. Say what could not be verified instead
of manufacturing confidence.

## Source

Adapted from Theo Browne's
[tstack modernize skill](https://github.com/t3dotgg/tstack/blob/6efae364201abc9d9f07443e9caa461f42e51090/skills/modernize/SKILL.md).
This adaptation distinguishes a requested rebase from reassessing an aging PR
and scopes branch updates to the PR's recorded remote head. The upstream MIT
notice is retained in [LICENSE](LICENSE).
