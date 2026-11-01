---
name: writing-skills
description: Use when creating new skills, editing existing skills, or verifying skills work before deployment
---

# Write Focused Skills

A skill should provide reusable guidance that helps with a specific class of
requests. Check existing skills first and improve the relevant one instead of
creating an overlapping workflow. Keep project-specific instructions in the
repository's existing guidance.

Use a folder containing `SKILL.md` and only the supporting resources it needs.
Frontmatter should provide a lowercase, hyphenated `name` and a `description`
explaining when to use the skill. Keep the main instructions concise and move
long reference material into supporting files loaded only when needed.

Describe the decisions, steps, and output that matter. Prefer one useful example
over repeated checklists, motivational text, or tables of forbidden responses.
Reference shared verification, documentation, and Git skills rather than copying
them. Preserve established user decisions and avoid mandatory approval stops for
routine authorized work.

Keep shared skills portable across harnesses. Use actual available tools and
permissions; put model selection and native settings in templates. Verify that
referenced skills and relative resources exist. Do not assume a tool, agent,
permission boundary, or upstream resource is installed.

For meaningful instruction changes, check realistic success, failure, and
ambiguous cases, using agent trials when available and proportionate. Compare
existing and proposed behavior where useful. For mechanical moves or wording
changes, use the relevant build, link, and content checks. Report verification
limits honestly and follow `verification-before-completion`.

Use `update-readme` when discovery, invocation, or installation changes. Installing,
publishing, or sending the skill elsewhere requires authorization beyond authoring
it unless the user already requested that action.
