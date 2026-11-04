---
name: update-readme
description: Checks whether README, AGENTS.md, or CLAUDE.md need updates after changes to behavior, setup, commands, or configuration. Use before committing such changes; skip internal-only refactors.
---

# Keep Project Guidance Current

When behavior, setup, or structure changes, check the README and existing
AGENTS.md or CLAUDE.md files that apply to the changed directories. Update only
affected guidance: commands, requirements, configuration, public behavior, or architecture.
Create new documentation when users or maintainers need guidance that existing
documents cannot accommodate clearly.

Keep examples consistent with the actual implementation and repository commands.
Review the rendered text or Markdown structure for broken links, stale references,
and confusing wording. Documentation-only edits do not need tests that restate
prose.

Complete this check before committing or handing off user-facing changes.
