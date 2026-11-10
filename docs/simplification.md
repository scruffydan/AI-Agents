# Proportionate Simplification

We selectively adapt ideas from [Ponytail](https://github.com/DietrichGebert/ponytail),
reviewed on 2026-11-10, into existing instructions. Ponytail is not a dependency.
The linked `main` sources are living references, not pinned runtime inputs.

## Adopted practices

- Check affected callers, tests and fixtures, configuration, and public exports
  before changing behavior or recommending simplification.
- Prefer existing project code, then platform or standard-library facilities,
  then installed dependencies before new code or dependencies. Reuse must fit
  the actual requirements and compatibility constraints.
- Preserve validation, failure handling, cleanup, security, accessibility, and
  persisted-data compatibility. Fewer lines alone do not establish improvement.
- State unchecked behavior and risks. Record consequential accepted shortcuts in
  an existing project record, with their impact and a reason to revisit them;
  read-only tasks only propose those notes in the response.

The [Ponytail core skill](https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail/SKILL.md)
provides the reuse order, affected-code inspection, safeguard preservation, and
shortcut ideas. Our proportional scope, report-only review limits, existing-record
preference, and verification reporting adapt those ideas to this repository.

## Boundaries

The `code-simplifier` remains a reviewer: it inspects and reports without edits,
installation, or executing project code and tests. Implementation choices also
belong in shared coding instructions so they apply while writing code. The
reviewer recommends relevant checks; it does not claim unexecuted checks passed.
Harness tool permissions differ, so report-only instructions alone do not create
a uniform sandbox. See the README's permission limits.

Keep existing verification guidance rather than adding a completion ritual,
mandatory new tests for every task, or a second debt ledger. Leave clear code
alone when no concrete simplification is supported by evidence.

The [upstream install guide](https://github.com/DietrichGebert/ponytail/blob/main/INSTALL.md)
offers plugins and hooks in addition to Markdown-only routes. We do not adopt
those integrations or the optional task metrics board: they add runtime,
configuration, and potentially sensitive local task data without an established
need here. Any future experiment should be separately authorized, preserve
existing configuration and project records, and treat metrics as disposable.

These changes do not introduce a planning mode or a knowledge store. Project
requirements, tasks, decisions, and verification stay in the target project's
existing records; an optional shared wiki can hold reusable lessons and links.
Acceptable downtime favors simpler operations, not loss of project data.
