# Go Refactor Implementation Plan

## Status

- This document supersedes the earlier planning notes for the Go refactor.
- It is intended to be complete enough that implementation can proceed phase by phase without referring back to the previous version.
- Scope includes `build.sh`, `install.sh`, and `opencode-init.sh`.

## Goal

Replace the current shell-heavy build and install flow with a small Go CLI that preserves current behavior, is easier for a solo maintainer to reason about, and makes adding a third platform such as Codex a renderer-level change instead of another round of shell branching.

## Why This Refactor Exists

The current shell scripts work, but they are carrying logic that shell is not a good long-term fit for:

- repeated argument parsing across scripts
- repeated provider validation and build mode decisions
- imperative platform branching instead of declarative platform data
- structured parsing of prompt frontmatter and include directives
- copy and overwrite flows that are hard to test in isolation

The refactor is justified only if the Go version ends up materially easier to maintain than the shell version.

## Non-Goals

- Do not redesign the source prompt format in `source/prompts/` during migration.
- Do not add Codex support until Claude and OpenCode parity is proven.
- Do not improve behavior and compatibility at the same time during Phase 1.
- Do not build a framework-heavy CLI.
- Do not force users to change documented commands immediately.

## Success Criteria

- Preserve all important user-facing behavior from `build.sh`, `install.sh`, and `opencode-init.sh`.
- Keep `source/prompts/`, `source/skills/`, `source/model-mappings.json`, and `source/opencode.json` as the source of truth.
- Reproduce the existing Claude and OpenCode `build/` output closely enough for diff-based review.
- Support existing install flows, including interactive and force-overwrite behavior.
- Keep wrappers or equivalent compatibility so current README commands still work during migration.
- Make a future platform addition mostly a descriptor and renderer task.

## Core Principle

Do not port the shell scripts line by line.

The Go version should be organized around:

- typed input model
- renderer per platform
- generic installer
- thin command layer

If the Go version becomes one large procedural translation of the shell scripts, stop the refactor.

## Current Behavior That Must Be Preserved

### Build

- `--work` model remapping behavior
- `--chatgpt-provider` validation and normalization behavior
- GPT provider normalization only for explicit GPT provider-prefixed models in non-work mode
- prompt discovery from `source/prompts/`
- skipping `AGENTS.md` and `_*.md` partials during prompt generation
- include expansion for `{{include:file.md}}`
- generation rules:
  - `subagent` -> Claude agent + OpenCode agent
  - `command` -> Claude command + OpenCode command
  - `mode` -> OpenCode primary agent only
- copying `source/prompts/AGENTS.md` into platform-specific base instruction files
- copying skills into both platform output trees
- writing `build/.unmapped-models`
- final build summary output

### Install

- install Claude only, OpenCode only, or both
- interactive selection when no target is specified
- interactive ChatGPT provider selection for OpenCode when applicable
- `--skip-build`
- `-y` / `--yes` force overwrite behavior
- copy files rather than symlink
- overwrite prompts for files and directories
- post-install inventory output
- warning replay for unmapped models

### OpenCode Init

- copy `source/opencode.json` to `~/.config/opencode/opencode.json`
- optional overwrite prompt or force mode
- configuration summary output

## Important Compatibility Constraint

The first Go build must preserve current generated output, including current omissions.

Example: some prompt files contain OpenCode frontmatter fields that the current shell build does not emit. The Go build should initially match current generated output rather than silently expanding behavior. Improvements can happen after parity is established.

## Recommended CLI Shape

```text
ai-agents build
ai-agents install
ai-agents init-opencode
```

## Recommended Repository Layout

```text
cmd/
  ai-agents/
    main.go
internal/
  app/
    build_cmd.go
    install_cmd.go
    init_opencode_cmd.go
  prompts/
    discover.go
    parse.go
    include.go
    model.go
  platforms/
    descriptor.go
    claude.go
    opencode.go
  build/
    build.go
  install/
    install.go
    overwrite.go
    summary.go
  files/
    copy.go
    fs.go
  testutil/
```

## Dependency Strategy

- Prefer the Go standard library for filesystem, JSON, path handling, CLI parsing, and text assembly.
- Use `encoding/json` for `source/model-mappings.json`.
- Use one YAML package for frontmatter parsing if needed. `gopkg.in/yaml.v3` is acceptable.
- Avoid CLI frameworks and configuration frameworks.
- Avoid introducing dependencies that solve problems the standard library already solves.

## Package Responsibilities

### `internal/app`

- Parse CLI args and flags.
- Dispatch subcommands.
- Own help output.
- Own interactive prompts only when they are command-level choices.

### `internal/prompts`

- Discover prompt files.
- Split frontmatter from body.
- Parse frontmatter into typed structs.
- Expand `{{include:file.md}}` directives.
- Load model mappings.
- Apply model provider selection and work-mode mapping.

### `internal/platforms`

- Define platform descriptors for Claude and OpenCode.
- Render prompt docs into platform-specific artifacts.
- Hide per-platform file naming and frontmatter formatting.

### `internal/build`

- Orchestrate build generation.
- Walk prompt inputs.
- Route each prompt to the correct renderer and artifact paths.
- Copy shared base instructions and skills.
- Write `.unmapped-models`.
- Produce final build summary data.

### `internal/install`

- Install built artifacts into target config directories.
- Reuse generic copy and overwrite logic.
- Handle force mode and interactive overwrite mode.
- Produce install summaries and warning replay.

### `internal/files`

- Filesystem helpers.
- Copy file and directory routines.
- Directory creation and existence checks.
- Safe overwrite helpers.

## Proposed Data Model

```go
type PromptType string

const (
    PromptTypeSubagent PromptType = "subagent"
    PromptTypeCommand  PromptType = "command"
    PromptTypeMode     PromptType = "mode"
)

type PromptDoc struct {
    Name        string
    Description string
    Type        PromptType
    Body        string
    Claude      ClaudeSpec
    OpenCode    OpenCodeSpec
}

type ClaudeSpec struct {
    Tools string
    Model string
}

type OpenCodeSpec struct {
    Mode            string
    Model           string
    Subtask         string
    Temperature     string
    ReasoningEffort string
    Permission      map[string]string
    Extra           map[string]any
}

type BuildOptions struct {
    Work            bool
    ChatGPTProvider string
    OutputDir       string
}

type Artifact struct {
    Path    string
    Content []byte
}
```

Notes:

- `Extra` exists so the parser can preserve future unknown frontmatter fields without immediately rendering them.
- The renderer should only emit fields currently produced by the shell implementation during parity phases.

## Command Responsibilities

### `ai-agents build`

- flags:
  - `--work`
  - `--chatgpt-provider`
  - optional `--output-dir` for verification and tests
- responsibilities:
  - discover prompts
  - parse frontmatter and body
  - expand includes
  - load mappings
  - normalize provider when applicable
  - render Claude and OpenCode outputs
  - copy base instructions and skills
  - write `.unmapped-models`
  - print summary

### `ai-agents install`

- flags:
  - `--claude`
  - `--opencode`
  - `--all`
  - `--skip-build`
  - `--work`
  - `--chatgpt-provider`
  - `-y`, `--yes`
- responsibilities:
  - choose targets interactively if none specified
  - choose ChatGPT provider interactively when needed
  - optionally run build internally
  - install generated files into target directories
  - handle overwrite behavior
  - print inventory and warnings

### `ai-agents init-opencode`

- flags:
  - `-y`, `--yes`
- responsibilities:
  - copy `source/opencode.json`
  - prompt before overwrite unless forced
  - print configuration summary

## Platform Descriptor Strategy

Each platform should declare the parts of the system that differ by platform instead of scattering branching logic.

Example shape:

```go
type PlatformDescriptor struct {
    Name             string
    AgentDir         string
    CommandDir       string
    SkillDir         string
    BaseInstruction  string
    SupportsCommands bool
    SupportsModes    bool
}
```

This lets future platforms describe their layout and supported artifact types without changing core orchestration code.

## Phase Plan

### Phase 0: Baseline and Freeze

Purpose:
- capture current behavior so parity can be judged against something concrete

Tasks:
- document current shell behavior that is intentionally preserved
- generate reference `build/` outputs using current shell scripts for:
  - default build
  - `--work`
  - `--chatgpt-provider opencode`
  - `--chatgpt-provider github-copilot`
- record any known quirks or omissions that must be preserved initially

Deliverable:
- a clear reference point for output and UX behavior

Acceptance gate:
- implementation work does not begin until the reference behavior is understood well enough to compare against it

### Phase 1: Build Parity

Purpose:
- replace `build.sh` with Go logic while preserving output

Tasks:
- create Go module and CLI skeleton
- implement prompt discovery
- implement frontmatter and body split
- implement include expansion
- implement model mapping load and provider normalization
- implement Claude and OpenCode renderers
- implement base instruction copy
- implement skill copy
- implement `.unmapped-models`
- implement final build summary

Deliverable:
- `ai-agents build` reproduces current generated output closely enough for diff-based review

Acceptance gate:
- compare shell output tree to Go output tree
- verify:
  - file presence
  - output paths
  - frontmatter fields emitted today
  - prompt body content
  - base instruction copies
  - skill copies
  - `.unmapped-models`

Stop condition:
- if this phase becomes branch-heavy or not materially simpler than shell, stop the rewrite and reassess

### Phase 2: Installer Engine

Purpose:
- replace `install.sh` with a generic Go installer

Tasks:
- define install target descriptors for Claude and OpenCode
- implement generic file and directory copy helpers
- implement overwrite prompt behavior for files and directories
- implement force mode
- implement interactive target selection
- implement interactive provider selection for OpenCode when needed
- call Go build logic directly when not using `--skip-build`
- print install inventories and warning replay

Deliverable:
- `ai-agents install` supports the same current install matrix

Acceptance gate:
- verify:
  - Claude only
  - OpenCode only
  - both
  - `--skip-build`
  - `--work`
  - each provider option
  - interactive target path
  - force overwrite mode

### Phase 3: OpenCode Init

Purpose:
- replace `opencode-init.sh` using the shared installer primitives

Tasks:
- implement single-file install flow for `source/opencode.json`
- reuse overwrite prompt logic
- reproduce current summary output

Deliverable:
- `ai-agents init-opencode` replaces current init behavior

Acceptance gate:
- verify:
  - clean install
  - overwrite prompt path
  - force overwrite path

### Phase 4: Compatibility Wrappers

Purpose:
- preserve existing documented commands while transitioning to the Go binary

Tasks:
- convert `build.sh` into a thin wrapper around the Go CLI
- convert `install.sh` into a thin wrapper around the Go CLI
- convert `opencode-init.sh` into a thin wrapper around the Go CLI
- keep help output and flags aligned as closely as practical

Deliverable:
- existing README commands still work

Acceptance gate:
- users can continue running existing shell entrypoints successfully

### Phase 5: Post-Parity Cleanup

Purpose:
- make the Go implementation nicer after behavior is stable

Tasks:
- remove temporary duplication introduced during parity work
- improve tests around malformed frontmatter and include cycles
- decide whether to support additional prompt frontmatter fields not emitted today
- tighten summaries and help text if needed
- simplify packages if any grew beyond their responsibility

Deliverable:
- a cleaner codebase with parity already preserved

Acceptance gate:
- cleanup changes do not regress build or install behavior

### Phase 6: Codex Support

Purpose:
- validate that the refactor actually made platform growth cheaper

Tasks:
- add a Codex platform descriptor
- add a Codex renderer
- add a Codex install target if needed
- avoid changing core build and install orchestration except where strictly necessary

Deliverable:
- third platform added with minimal core changes

Acceptance gate:
- Codex support can be added without a new explosion of branch logic

## Testing and Verification Strategy

### Unit Tests

- frontmatter split behavior
- include expansion
- nested include behavior
- missing include handling
- provider normalization
- work mapping lookup
- unmapped model tracking
- Claude rendering
- OpenCode rendering

### Golden Tests

- subagent prompt rendering
- command prompt rendering
- mode prompt rendering
- permission block rendering
- unmapped model rendering behavior

### Integration Tests

- build into temp directories
- compare generated file trees
- install into temp home directories
- verify overwrite prompt and force behavior

### Manual Verification Matrix

- `build`
- `build --work`
- `build --chatgpt-provider opencode`
- `build --chatgpt-provider github-copilot`
- `install --claude`
- `install --opencode`
- `install --all`
- `install --skip-build`
- `install --opencode --work`
- `init-opencode`
- overwrite prompts and force mode

## Risks

### Medium Risk

- YAML parsing differs subtly from current `yq` behavior
- output formatting changes create noisy diffs
- interactive UX drifts from existing shell behavior
- compatibility wrappers drift from Go subcommand flags over time

### Low Risk

- generic copy logic is simpler in Go than shell
- model mapping is simpler in Go than shell plus `jq`
- renderer separation should reduce future platform complexity

## Risk Mitigations

- keep Phase 1 focused on parity, not improvements
- use diff-based acceptance gates
- add `--output-dir` to support isolated verification
- test install behavior against temp directories instead of real user config locations
- keep wrappers until the Go path has been manually exercised multiple times

## Maintainability Guardrails

- no package should both parse prompts and install files
- no renderer should read files directly
- no installer should know frontmatter parsing rules
- avoid premature interfaces
- avoid utility dumping grounds
- prefer explicit structs over untyped maps except for preserving unknown fields
- prefer boring code over generic abstractions

## Decisions to Lock Early

### 1. Frontmatter parsing

Recommendation:
- use a small YAML dependency rather than building a parser in-house

Reason:
- current frontmatter already has enough nesting that a custom parser is likely to create more maintenance burden than it removes

### 2. Wrapper strategy

Recommendation:
- keep thin shell wrappers during migration

Reason:
- preserves existing commands and reduces rollout risk

### 3. Acceptance gate

Recommendation:
- treat `build/` diffs and install UX parity as the primary migration gate

Reason:
- this keeps the refactor honest and avoids architecture discussions detached from actual output

## Stop Conditions

Stop and reassess if any of the following happens:

- Phase 1 cannot reproduce the current build output cleanly enough to review
- the Go code starts mirroring shell branches line by line
- package boundaries collapse into one procedural command package
- the refactor does not feel materially easier to understand than the shell scripts
- adding Codex still appears likely to require core branching changes instead of a descriptor and renderer

## Recommended First Implementation Slice

Start with only this:

1. create the Go module and CLI skeleton
2. implement `ai-agents build`
3. render Claude and OpenCode output into a temp build directory
4. diff against current shell build output

If this slice is not clearly simpler to reason about than the shell version, stop before implementing install.

## Suggested Next Step

Implement Phase 1 only on the `go-refactor-experiment` branch and evaluate the result before touching install behavior.
