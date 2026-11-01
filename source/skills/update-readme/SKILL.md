---
name: update-readme
description: Use when making code changes that affect user-facing behavior, before committing or pushing - reminds AI to check if README and existing AGENTS.md files need updates to stay in sync with implementation changes
---

# Keep Project Guidance Current

When behavior, setup, or structure changes, check the README and existing
AGENTS.md files that apply to the changed directories. Update only affected
guidance: commands, requirements, configuration, public behavior, or architecture.
Do not create new documentation merely to satisfy a checklist.

Keep examples consistent with the actual implementation and repository commands.
Review the rendered text or Markdown structure for broken links, stale references,
and confusing wording. Documentation-only edits do not need tests that restate
prose.

Complete this check before committing or handing off user-facing changes. Reuse a
valid check from this session while its relevant inputs are unchanged. Use
`verification-before-completion` for test and build evidence instead of repeating
that workflow here.
