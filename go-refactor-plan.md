# Go Refactor Implementation Plan

## Status

- This plan now reflects the Go-first direction already implemented in the repo.
- The project is no longer optimizing for shell-output parity or preserving the old shell UX.
- `build.sh`, `install.sh`, and `opencode-init.sh` are compatibility wrappers around the Go CLI.

## Goal

Replace the shell-driven workflow with a small, maintainable Go CLI that keeps the important workflows intact while allowing the command UX, summaries, and internal structure to get simpler.

## Direction Change

The original draft leaned heavily on parity with the shell scripts.

That is no longer the right constraint.

What matters now:

- preserve the source of truth in `source/`
- preserve the core workflows users rely on
- make build/install behavior easy to test in Go
- keep the wrapper scripts working during the transition
- optimize for maintainability, not line-by-line migration fidelity

What no longer matters:

- reproducing shell output formatting exactly
- preserving the old interactive wording
- mirroring the shell architecture in Go
- blocking cleanup until every shell quirk is copied

## Current Implementation Shape

```text
cmd/
  ai-agents/
    main.go
internal/
  app/
    app.go
  buildsys/
    build.go
    build_test.go
  files/
    fs.go
  install/
    install.go
    install_test.go
    opencode.go
  platforms/
    render.go
  prompts/
    prompts.go
    prompts_test.go
```

## What Is Already Done

### Build

- `ai-agents build` exists and is the primary build path.
- Prompt discovery skips `AGENTS.md` and `_*.md` partials.
- Frontmatter parsing happens in Go.
- `{{include:file.md}}` expansion happens in Go.
- Claude and OpenCode artifacts are rendered in Go.
- Base instructions and skills are copied in Go.
- `build/.unmapped-models` is written in Go.
- Wrapper script `build.sh` now delegates to the Go CLI.

### Install

- `ai-agents install` exists.
- Claude-only, OpenCode-only, and both-target installs are supported.
- Interactive target selection is supported when no target is specified.
- Interactive GPT provider selection is supported for OpenCode when relevant.
- `--skip-build`, `--work`, `--chatgpt-provider`, and `-y` / `--yes` are supported.
- Copy and overwrite logic is implemented in Go.
- Wrapper script `install.sh` now delegates to the Go CLI.

### OpenCode Init

- `ai-agents init-opencode` exists.
- Overwrite prompting and force mode exist.
- Wrapper script `opencode-init.sh` now delegates to the Go CLI.

### Verification Coverage

- Unit coverage exists for prompt parsing, include expansion, model mapping, and provider selection.
- Temp-home integration coverage exists for install and init overwrite flows.

## Core Principles

1. Do not port shell logic line by line.
2. Prefer small, explicit Go code over shell-compatible cleverness.
3. Preserve workflows, not presentation details.
4. Keep wrappers thin and disposable.
5. Add tests before expanding scope.

## Success Criteria

- Users can still run `./build.sh`, `./install.sh`, and `./opencode-init.sh` successfully.
- Users can also call `ai-agents build`, `ai-agents install`, and `ai-agents init-opencode` directly.
- Generated artifacts remain structurally correct for Claude Code and OpenCode.
- Install flows work against temp home directories without touching real user config.
- Overwrite behavior is deterministic and testable.
- Future platform additions mainly affect prompt rendering and install descriptors, not command orchestration.

## Non-Goals

- Do not preserve shell output text exactly.
- Do not preserve every historical shell quirk unless it protects a real workflow.
- Do not add a CLI framework.
- Do not add Codex support yet.
- Do not redesign prompt authoring in `source/prompts/` during this phase.

## Architecture Boundaries

### `internal/app`

- Parse command args.
- Own help text and command UX.
- Dispatch subcommands.

### `internal/prompts`

- Load prompt files.
- Split frontmatter and body.
- Expand includes.
- Load model mappings.

### `internal/platforms`

- Render platform-specific frontmatter and documents.
- Keep Claude/OpenCode output differences isolated.

### `internal/buildsys`

- Orchestrate generation.
- Copy shared assets.
- Write build summaries and unmapped model output.

### `internal/install`

- Install artifacts into target config directories.
- Handle overwrite prompts and force mode.
- Own temp-home-friendly install behavior.

### `internal/files`

- Provide filesystem helpers.
- Keep copy/write/reset logic boring and reusable.

## Remaining Work

### Near Term

- Add more integration coverage for full interactive install scenarios.
- Add targeted tests for CLI help text and command dispatch.
- Refine build/install summaries where they still feel noisy or inconsistent.
- Consider extracting install summary structs if reporting logic grows.

### Medium Term

- Split `internal/prompts/prompts.go` if parsing and include logic grow much further.
- Split `internal/platforms/render.go` if Claude/OpenCode rendering diverges.
- Add a real packaged binary build path instead of relying on `go run` in wrappers.

### Later

- Reassess whether wrappers should remain or whether the repo should document the Go CLI as the primary entrypoint.
- Add a third platform only after the current package boundaries still feel clean.

## Verification Strategy

### Required Before Claiming Completion

- `go test ./...`
- wrapper help checks for install/init commands
- at least one end-to-end build run through `./build.sh`

### Preferred Ongoing Checks

- temp-home install runs for Claude + OpenCode
- temp-home init-opencode runs
- spot checks of generated artifacts for modes, commands, and subagents

## Stop Conditions

Stop and simplify if any of the following happens:

- the Go code starts imitating shell branching instead of using clear structs and helpers
- help/output cleanup gets blocked by parity arguments
- a package begins mixing parsing, rendering, and installation concerns
- tests become harder to write than the code is to change
- adding another platform still appears to require cross-cutting command changes

## Recommended Next Step

Treat the Go CLI as the product and the shell scripts as temporary wrappers.

All future refactor work should improve the Go implementation directly, then decide whether the wrappers still add enough value to keep.
