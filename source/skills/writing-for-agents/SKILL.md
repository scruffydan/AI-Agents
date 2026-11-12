---
name: writing-for-agents
description: Author or revise agent instruction artifacts such as AGENTS.md, skill instructions, and agent prompts. Use for their triggers, structure, constraints, and completion criteria, not ordinary coding answers or general prose editing.
---

# Writing for Agents

Make instructions easy to select, follow, and verify. Complement the platform's
skill-creation workflow when available; use its packaging and validation guidance
rather than scaffolding a competing system. Follow the target repository's format.

## Establish the contract

Read the artifact and applicable instructions, relevant callers or references,
and the user's intended outcome. Identify who consumes it, when it is loaded,
and which decisions it should change. Preserve existing safeguards and deliberate
exceptions when shortening or reorganizing text.

Keep the current task's scope and permissions. A request to review instructions
remains read-only; examples and reference material do not grant authorization.
Drafting a workflow does not authorize executing it, installing it, or publishing
it. Reuse established authorization for routine choices; ask only when a material
choice is unresolved or an action exceeds that authorization.

## Write precise discovery text

For a skill description, name the capability and the concrete requests that should
select it. Include a nearby exclusion when it prevents likely confusion. Keep
procedural detail in the body. For a reference pointer, say what the file contains
and the condition under which to read it; avoid vague labels like "more details."

Check discovery against a realistic matching request and a nearby nonmatching
request. The description must fit the actual instructions without promising
unsupported behavior or attracting every task in the same broad domain.

## Keep the core small

Put shared purpose, essential constraints, and instructions needed on every route
in the entry point. Group each rule with its conditions, exceptions, and rationale
when that rationale affects decisions. Use consistent domain terms and direct
verbs. Replace vague goals such as "be thorough" with observable outcomes.
Remove repetition and generic advice that does not change the agent's decisions.

Move substantial branch-specific procedures, schemas, or examples into focused
files linked relatively from the entry point. State when to read each file; load
only the selected branch. Keep essential authorization and safety boundaries in
the core so they cannot disappear behind an optional reference. A short workflow
needs no extra routing layer or placeholder reference files.

For example, a document workflow could say: "For tracked changes, read
`references/redlining.md` for revision-marking and preservation rules." Create
and link that file only if the workflow actually supports that branch.

Prefer desired actions and decision criteria to long lists of prohibitions.
Retain explicit prohibitions where a boundary matters, including read-only scope,
secrets, destructive actions, or external writes. Do not add blanket approval
gates, mandatory delegation, or permission to perform external actions.

## Make completion observable

State what deliverable or behavior establishes completion and what evidence can
support it. Distinguish required outcomes from optional improvements. For example,
"Report the changed files and the checks actually run, with their results" is
checkable; "ensure everything is correct" is not.

Review each route for missing inputs, ambiguous decisions, unreachable references,
and unsupported completion claims. Check relative links from the containing file,
metadata against the target format, and examples against the stated boundaries.
Use existing relevant validators or safe task examples proportionate to the
change; avoid tests that merely assert prose. Report static inspection separately
from observed behavior, and identify untested or blocked checks honestly.

## Source

Adapted selected instruction-writing ideas from Matt Pocock's
[writing-for-agents](https://github.com/mattpocock/skills/blob/321658273cb1d20b76026717d027d505790106d4/skills/productivity/writing-for-agents/SKILL.md):
precise triggers, progressive disclosure, grouped rules, and checkable completion.
See [LICENSE](LICENSE) for the upstream MIT notice. This is a focused adaptation,
not an import of the upstream framework.
