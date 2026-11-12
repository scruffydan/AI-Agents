---
name: to-tickets
description: Turn an established plan into independently verifiable vertical implementation slices with acceptance criteria, verification, and true dependencies. Use when breaking planned work into tickets; small changes can stay as one task.
---

# Turn a Plan into Tickets

Convert an established plan into the smallest useful set of implementation slices.
Each slice should deliver a narrow, complete behavior that can be demonstrated
and verified through the relevant layers. Avoid separate database, backend, and
UI tickets when none would establish a useful outcome on its own. Infrastructure
or internal changes can deliver an observable operational or developer outcome.
If one focused task suffices, keep it as one; do not manufacture a backlog.

## Reuse the plan

Read the relevant plan, repository guidance, affected code, and verification
commands within current permissions. Reuse accepted scope, decisions, and
constraints rather than reopening them. Use the existing task record and
`project-context` workflow when available; avoid parallel records or separate
debt ledgers. `thorough-plan` develops an approach; this skill decomposes an
established approach. If the plan lacks a consequential decision, identify the
specific gap and continue slicing unaffected work. Ask only when the answer
materially changes the slices; label assumptions and proposals as such.

## Choose slices and dependencies

Start with the smallest complete path that proves the approach, then extend
behavior in useful increments. Include integration, error handling, and relevant
tests in each slice rather than postponing them to a final integration ticket.
Keep the project working between slices. Scope slices for reviewable outcomes,
not a fixed duration, file count, or number of tickets.

Record a dependency only when another slice must supply a concrete capability,
interface, data state, or decision before this slice can complete. Name that
prerequisite and explain why. Distinguish a preferred order from a true blocker;
mark independent slices explicitly. Break dependency cycles by narrowing scope
or agreeing on a stable interface. Do not claim independence when verification
still requires unfinished work. For unresolved external blockers, name the missing
input, affected slices, and what would unblock them without inventing an owner
or deadline.

Where persisted data or compatibility warrants staged change, consider
expand–migrate–contract:

- **Expand:** add compatible interfaces or storage while existing consumers work.
- **Migrate:** move consumers or backfill data in verifiable increments; include
  coexistence, failure recovery, and data preservation checks as relevant.
- **Contract:** remove old paths only after evidence shows migration is complete
  and the agreed compatibility window has ended.

Make those prerequisites explicit. Use a simpler direct change when it meets the
project's compatibility and data requirements; this pattern is not a required
architecture.

## Present actionable tickets

Default to the conversation. For each slice, provide a concise title and:

- **Outcome:** the observable behavior or capability and its link to the plan's
  requirement or goal.
- **Scope:** included work, relevant components, and boundaries needed to prevent
  overlap or unplanned expansion.
- **Acceptance criteria:** observable success and relevant failure, compatibility,
  or data preservation behavior; avoid vague criteria such as “works correctly.”
- **Verification:** specific existing checks, proportionate new tests, or manual
  observations that would establish the criteria. Label planned checks as planned;
  a drafted ticket is not completion evidence.
- **Dependencies/blockers:** prerequisite slice IDs and reasons, unresolved inputs,
  or “None.” Distinguish completion dependencies from work that can start now.

Use stable IDs when useful for cross-references. Keep enough context in each ticket
for implementation without reconstructing the whole conversation; link the source
plan and accepted decisions instead of duplicating them. Finish by checking that
in-scope requirements are covered, every ticket has an independently verifiable
outcome, dependencies are justified, and no unrelated work has slipped in.

Writing files or updating a tracker requires authorization for that destination;
reuse authorization already given. Ticket decomposition alone does not authorize
setup, external ticket creation, publication, implementation, or delegated execution.
When saving is authorized, update the existing task record rather than creating a
second ledger. Report what was actually saved or created and any remaining gaps.

## Source

Adapted from selected ideas in Matt Pocock's
[to-tickets skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-tickets/SKILL.md):
vertical slices, explicit blockers, and expand–migrate–contract.
The upstream MIT notice is retained in [LICENSE](LICENSE).
