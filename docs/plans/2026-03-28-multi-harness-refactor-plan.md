# Multi-Harness Refactor Plan

Date: 2026-03-28

## Goal

Refactor AI-Agents so prompts, subagents, commands, modes, and skills are authored once and rendered for multiple harnesses.

The new system should:

- treat OpenCode as the default harness
- support Claude and Codex as first-class targets
- make future harnesses cheap to add
- switch model selections with `--work`
- allow a breaking CLI and output shape if that produces a cleaner design

## Executive Recommendation

Create a new branch from `refactor/python-build-system`, but do not preserve its current architecture.

Use it as a small bootstrap only, then rebuild around:

- a harness registry
- a harness-neutral source schema
- logical model profiles instead of hard-coded model strings
- golden tests for generated output
- OpenCode-first CLI defaults

Steal the Go branch's strongest ideas:

- explicit pipeline stages
- test coverage mindset
- install safety
- narrow modules with clear responsibilities

Do not keep either branch's two-harness-specific core model.

## Why A Third Path Is Better

Both refactor branches still encode the wrong center of gravity.

- the Go branch has better package structure, but its domain model is hard-coded around `Claude` and `OpenCode`
- the Python branch is smaller and easier to reshape, but its renderer still assumes `Claude` plus `OpenCode-like everything else`
- both branches keep harness-specific assumptions in prompt content and skills, which blocks real reuse

Because backward compatibility is not required, the best move is a clean architecture that makes harnesses explicit extension points instead of special cases.

## Product Decisions

These decisions should be treated as locked unless a later plan intentionally changes them.

1. OpenCode is the default harness for `build` and `install`
2. Claude and Codex are supported by the initial architecture, even if Codex lands after OpenCode parity
3. `--work` switches model resolution to a work environment mapping layer
4. Interactive harness-selection menus are not required
5. Backward compatibility with `build.sh`, `install.sh`, and old output conventions is not required
6. Install overwrite prompts remain explicit unless the user passes `--force`

## Success Criteria

The refactor is successful when all of the following are true:

- prompts, commands, modes, and skills can be rendered from one shared source tree
- adding a new harness does not require editing the core parser or orchestration flow
- OpenCode builds with no harness flags
- `--work` changes resolved models without rewriting source prompt files
- Claude and Codex support fit the same architecture as OpenCode
- generated output is covered by golden tests
- install behavior is safe and independently tested
- harness-specific wording is isolated to overrides instead of being mixed through shared bodies

## Non-Goals

- preserving the current shell wrapper UX
- preserving the current frontmatter schema
- preserving current install prompts or command names exactly
- keeping `main` as the behavior contract in places where the new architecture is cleaner

## Recommended Repository Layout

Use Python, but with a multi-module layout instead of a single script.

```text
ai_agents/
  cli.py
  repo.py
  fs.py
  domain/
    documents.py
    harnesses.py
    models.py
    options.py
  content/
    loader.py
    schema.py
    includes.py
    validation.py
  profiles/
    resolver.py
  render/
    base.py
    opencode.py
    claude.py
    codex.py
  build/
    service.py
  install/
    service.py
    targets.py
tests/
  test_schema.py
  test_includes.py
  test_profiles.py
  test_render_opencode.py
  test_render_claude.py
  test_render_codex.py
  test_build_golden.py
  test_install.py
  fixtures/
    source/
    expected/
```

## Core Domain Model

The core model should stop encoding named harnesses directly.

### `Document`

Represents a source prompt, command, mode, or skill.

- `name`
- `description`
- `kind` (`subagent`, `command`, `mode`, `skill`, `base`)
- `body`
- `model_profile`
- `shared_metadata`
- `targets: dict[str, TargetOverride]`
- `source_path`

### `TargetOverride`

Optional harness-specific metadata or content overrides.

- `enabled`
- `metadata`
- `body_append`
- `body_prepend`
- `partials`

### `HarnessSpec`

Defines how one harness behaves.

- `name`
- `default_selected`
- `supports_modes`
- `output_layout`
- `install_target`
- `base_filename`
- `skill_layout`
- `renderer`
- `capabilities`

### `ModelProfile`

Logical model intent, not a concrete model string.

- `name` (`default`, `deep_review`, `creative`, `planner`)
- per-environment values (`default`, `work`)
- per-harness concrete settings

### `BuildOptions`

- `repo_root`
- `output_dir`
- `selected_harnesses`
- `environment` (`default`, `work`)
- `include_skills`
- `include_base_files`

### `InstallOptions`

- `repo_root`
- `build_dir`
- `selected_harnesses`
- `force`
- `skip_build`
- `environment`

## Source Schema

Use TOML frontmatter and keep the markdown body as the shared instruction body.

The schema should move from harness names as top-level fields to a neutral `targets` section.

### Example

```toml
+++
description = "Security review specialist for finding vulnerabilities."
kind = "subagent"
model_profile = "deep_review"

[shared]
tags = ["review", "security"]

[targets.opencode]
role = "agent"
mode = "subagent"
reasoning_effort = "high"

[targets.opencode.permission]
edit = "deny"
bash = "deny"
question = "deny"

[targets.claude]
role = "agent"
tools = "Read, Glob, Grep"

[targets.codex]
role = "agent"
sandbox = "read-only"
approval_policy = "on-request"
+++
```

### Schema Rules

1. `kind` is shared and required
2. `model_profile` is shared and preferred over concrete model strings
3. `targets.<harness>` is optional; absence means the document is not rendered for that harness
4. shared body text should be harness-neutral by default
5. harness-specific wording belongs in target overrides or partials, not mixed through the main body
6. the parser validates unsupported metadata keys per harness

## Content Strategy

The source content needs a real cleanup, not just a new builder.

### Rules For Shared Bodies

- remove direct sections like "For Claude Code" and "For OpenCode" from shared prompt bodies
- write task intent once in neutral language
- move harness-specific invocation syntax into target overrides or partial includes
- keep skills generic unless a skill is explicitly harness-specific

### Allowed Harness-Specific Content

Harness-specific content is allowed only in one of these places:

- `targets.<harness>.body_prepend`
- `targets.<harness>.body_append`
- `partials/<document>/<harness>.md`

### Lint Rule

Add a content lint that fails if shared prompt bodies contain patterns like:

- `For Claude`
- `For OpenCode`
- `@code-`
- `Task tool`

unless the file is explicitly marked as harness-specific.

## Model Resolution Design

`--work` should not mutate raw source model strings. It should select a different environment for logical model profiles.

### Recommended Model Files

`source/model-profiles.toml`

```toml
[profiles.deep_review.default.opencode]
model = "openai/gpt-5.4"
reasoning_effort = "high"

[profiles.deep_review.work.opencode]
model = "google-vertex-anthropic/claude-opus-4-5@20251101"
reasoning_effort = "high"

[profiles.deep_review.default.claude]
model = "claude-opus-4-5"

[profiles.deep_review.work.claude]
model = "claude-opus-4-5"

[profiles.deep_review.default.codex]
model = "openai/gpt-5.4"
sandbox = "read-only"
```

### Resolution Rules

1. document picks a `model_profile`
2. build selects environment `default` unless `--work` is set
3. resolver returns harness-specific concrete settings
4. target override metadata can add non-model harness settings
5. if a harness lacks a profile entry, build fails with a validation error

This makes `--work` a clean environment switch rather than an OpenCode-specific rewrite.

## Harness Registry Design

Each harness should be registered in one place.

### Required Spec Fields

- output root name
- document kind to output directory mapping
- supported metadata keys
- install target
- base file output name
- renderer function
- capabilities such as `supports_modes`, `supports_skills`, `supports_permissions`

### Initial Harness Set

#### OpenCode

- default harness
- supports subagents, commands, modes, skills, base instructions
- install target: `~/.config/opencode`

#### Claude

- supports subagents, commands, skills, base instructions
- no mode output unless a Claude-specific equivalent is later defined
- install target: `~/.claude`

#### Codex

- supports subagents or equivalent agent files, commands if supported, skills if supported by the harness
- install target: `~/.codex`
- implementation can initially be minimal as long as the architecture supports it cleanly

## CLI Shape

The CLI can be simpler and more explicit than the current scripts.

### Commands

```text
ai-agents build [--harness <name> ...] [--all] [--work] [--output <dir>]
ai-agents install [--harness <name> ...] [--all] [--work] [--skip-build] [--force]
ai-agents init opencode [--force]
ai-agents list harnesses
ai-agents lint
```

### Defaults

- `build` with no harness flags builds OpenCode only
- `install` with no harness flags installs OpenCode only
- `--all` builds or installs every registered harness
- `--work` is equivalent to `--environment work`

### CLI Notes

- remove interactive harness selection menus
- keep overwrite confirmation prompts for installs
- keep command help snapshot-tested
- shell wrappers are optional compatibility conveniences, not the primary interface

## Render Pipeline

Keep the build stages explicit and testable.

1. find repo root
2. load source documents
3. expand includes and partials
4. validate schema
5. resolve model profiles for selected environment and harnesses
6. render harness-specific artifacts
7. copy base instructions and skills
8. write output tree
9. optionally install

Each stage should be pure where possible and should return explicit errors.

## Install Design

Install behavior should be separate from rendering.

### Rules

- install never mutates build output
- `--skip-build` uses the given build directory as-is
- overwrite prompts remain explicit unless `--force` is passed
- OpenCode config initialization stays opt-in
- install tests cover accept, decline, and force flows

## Testing Strategy

This refactor should not merge without real tests.

### Unit Tests

- schema parsing
- include expansion
- target override merging
- model profile resolution
- harness capability validation

### Golden Tests

- OpenCode output for representative prompts, commands, modes, and skills
- Claude output for representative prompts, commands, and skills
- Codex output fixtures once renderer lands
- base instruction and skill copy output

### Behavioral Tests

- `build` default builds OpenCode only
- `build --all` builds all registered harnesses
- `build --work` switches environments correctly
- `install --skip-build` preserves current build output
- overwrite prompt handling
- help output snapshots

### Content Lint Tests

- fail if shared prompt bodies contain harness-specific instruction markers
- fail if documents reference unknown harnesses
- fail if a referenced `model_profile` is missing

## Migration Plan

Implement the refactor in phases.

### Phase 0 - Branch Setup

- branch from `refactor/python-build-system`
- keep the existing source content as migration input only
- add the new package layout beside `build.py`

Exit criteria:

- new branch created
- package skeleton checked in
- no behavior claims yet

### Phase 1 - Lock The New Contract

- define the new CLI shape
- define the new frontmatter schema
- define harness registry interfaces
- define model profile files and environment resolution rules

Exit criteria:

- design accepted
- schema examples checked in under `tests/fixtures/source`

### Phase 2 - Build OpenCode First

- implement parser, validator, resolver, and OpenCode renderer
- migrate existing source prompts to the new schema
- remove OpenCode-specific assumptions from shared bodies
- add OpenCode golden tests

Exit criteria:

- `build` default emits OpenCode only
- `--work` switches OpenCode models through profile resolution
- OpenCode golden tests pass

### Phase 3 - Add Claude On The Same Abstractions

- implement Claude renderer with no parser changes
- migrate any Claude-specific instruction text into target overrides
- add Claude golden tests

Exit criteria:

- Claude support requires only renderer and target metadata
- no new harness-specific branches in parser or build orchestration
- Claude golden tests pass

### Phase 4 - Add Codex As The Extensibility Proof

- implement Codex harness spec and renderer
- decide the minimal viable artifact shape for Codex
- add Codex fixtures and tests

Exit criteria:

- Codex lands without changing the shared source schema
- Codex renderer uses the same pipeline as OpenCode and Claude
- codex-specific metadata is validated cleanly

### Phase 5 - Replace Old Entry Points

- make the new Python CLI the supported interface
- optionally keep tiny wrapper scripts that pass through to the CLI
- update README after actual behavior is implemented

Exit criteria:

- documentation matches real commands
- old architecture code is removed

## Recommended File-By-File Migration

### 1. Replace Source Prompt Schema

Move from:

- top-level `claude`
- top-level `opencode`

To:

- `model_profile`
- `shared`
- `targets.<harness>`

### 2. Rewrite Shared Prompt Bodies

Start with the files most obviously coupled to current harnesses:

- `source/prompts/code-full-review.md`
- `source/prompts/docs-fetcher.md`
- `source/prompts/explore.md`
- `source/prompts/sidebar.md`
- `source/prompts/AGENTS.md`
- `source/skills/using-code-review/SKILL.md`
- `source/skills/using-docs-fetcher/SKILL.md`
- `source/skills/writing-skills/SKILL.md`

### 3. Introduce Model Profiles

Move concrete model strings out of most prompt files and into shared profile config.

### 4. Add A Harness Linter

Catch source coupling before it lands in generated output.

## Risks And Mitigations

### Risk: Content migration is larger than the builder refactor

Mitigation:

- treat prompt-body cleanup as a first-class workstream
- add lint rules early

### Risk: Codex support is underdefined

Mitigation:

- define `HarnessSpec` capabilities first
- allow Codex renderer to start minimal
- do not let Codex uncertainty distort the shared schema

### Risk: `--work` becomes another special case

Mitigation:

- implement environment-based model resolution before migrating prompts
- forbid raw model rewrites inside renderers

### Risk: Single-file Python entropy returns

Mitigation:

- reject new feature work in `build.py`
- move logic into modules from the start

## Acceptance Checklist

- [ ] OpenCode is the default harness
- [ ] Claude and Codex fit the same harness registry
- [ ] prompt schema is harness-neutral
- [ ] shared bodies are free of harness-specific instruction text
- [ ] `--work` resolves logical model profiles by environment
- [ ] golden tests cover generated output
- [ ] install tests cover overwrite safety
- [ ] docs describe the actual CLI

## Final Recommendation

Start from `refactor/python-build-system`, but only as a bootstrap.

The target should be a new Python architecture with:

- Go branch discipline
- Python branch size and readability
- a harness registry instead of hard-coded named harnesses
- model profiles instead of embedded concrete model strings
- OpenCode-first defaults

If the branch cannot add Codex without parser changes, the refactor is not finished.
