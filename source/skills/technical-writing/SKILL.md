---
name: technical-writing
description: Write or revise technical documentation, tutorials, how-to guides, reference material, and explanations so readers can understand and complete their task.
---

# Technical Writing

Use this skill to shape the requested documentation. `update-readme` addresses
whether project guidance needs updating; this skill addresses how to write it.
Preserve the requested scope, existing conventions, and read-only boundaries.
Writing a procedure does not authorize executing it or publishing the result.

## Start with the reader's task

Identify the audience, what they already know, and what they should be able to do
or understand afterward. Reuse context and existing docs; ask only when missing
information would materially change the instructions. State consequential
assumptions rather than quietly treating them as facts.

Choose a useful emphasis, not a mandatory template:

- A tutorial teaches through a guided example with a visible result.
- A how-to helps someone complete a specific task with actionable steps.
- Reference makes exact syntax, options, defaults, and constraints easy to find.
- Explanation develops the reasons, concepts, and trade-offs behind behavior.

Mix these when it helps the reader. Keep the main task easy to follow; link to
long background or exhaustive reference instead of interrupting every step.

## Make the common path usable

Lead with the purpose and common case. Put prerequisites before the steps that
need them: supported versions, access, setup, inputs, and starting directory or
state. Include only prerequisites relevant to this task. Put important conditions
and consequences before the action, especially when data or availability is at
risk. Distinguish required steps from optional alternatives.

Use actual product names, UI labels, paths, flags, and identifiers consistently.
Make examples coherent and commands usable in the stated shell and environment.
Label placeholders and explain their replacements; never substitute real secrets
or private data. Show expected output or another observable success condition
where readers need it to decide whether to continue.

Group instructions by the reader's goal. Use numbered steps for order-dependent
actions, one main action per step, with its immediate result or explanation nearby.
Place likely failures beside the relevant step or in a short troubleshooting
section: recognizable symptom, likely cause, and a safe recovery or next diagnostic
check. Explain when to stop rather than blindly retrying a destructive action.

## Keep claims grounded

Check commands, defaults, examples, and behavior against the relevant code,
configuration, tests, or primary documentation for the installed or targeted
version. Cite sources near claims that need attribution or further verification;
include version or date context when behavior can change. Do not silently replace
the project's version with the latest release.

Separate verified facts, inferences, and unknowns. If a command cannot be checked,
state the limit; do not invent plausible output or imply it ran. Documentation
work alone does not authorize external writes, installation, or risky execution.
Use safe checks within the task's permissions and report what was actually checked.

## Edit for understanding

Use direct verbs, familiar terms, and concrete examples. Define unfamiliar terms
when they first matter. Address the reader as “you” when useful, and name the actor
when responsibility would otherwise be unclear. Keep sentences focused without
forcing a fixed length or stripping necessary qualifications.

Replace vague pronouns, ambiguous modifiers, and dense noun strings with explicit
relationships. Use headings that name the task or concept, code formatting for
literal identifiers, and lists or tables when they make steps or choices easier to
scan. Preserve technical precision while removing repetition and unnecessary jargon.

Read the result from the stated starting point: are inputs available, steps in
order, examples consistent, links useful, and success and recovery recognizable?
Scale verification to the change; do not add tests that merely assert prose.

## Source

Adapted from selected ideas in Lauren Tan's
[pstack technical-writing skill](https://github.com/cursor/plugins/blob/ec569379616a4826b98f0f0a205dd3411b573611/pstack/skills/technical-writing/SKILL.md),
under the MIT license. See [LICENSE](LICENSE) for the upstream notice. This is a
focused adaptation, with no dependency on other upstream skills.
