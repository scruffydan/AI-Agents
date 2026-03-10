# Go Refactor Plan

## Goal

Replace the current shell-heavy build and install flow with a Go-based CLI that preserves all existing behavior while making it easier to add a third platform such as Codex.

This plan does not change code yet. It defines the target design, migration path, and verification strategy.

## Current Problems

- `build.sh` and `install.sh` duplicate argument parsing, provider validation, target-specific branching, copy behavior, and summary output.
- Platform behavior is encoded in imperative branches rather than declarative data, which makes a third platform expensive to add.
- Shell is doing structured parsing, templating, and file orchestration work that is difficult to test and easy to drift.
- The scripts are tightly coupled: `install.sh` knows too much about `build.sh` internals.

## Success Criteria

- Preserve all current user-facing behavior from `build.sh`, `install.sh`, and `opencode-init.sh`.
- Keep the current source format in `source/prompts/`, `source/skills/`, `source/model-mappings.json`, and `source/opencode.json`.
- Support the existing Claude and OpenCode outputs exactly or very close enough to diff cleanly.
- Make adding `codex` mostly a renderer/descriptor addition instead of a new branch of shell logic.
- Be testable with repeatable build/install verification.

## Recommended Architecture

Use one Go CLI with subcommands:

```text
ai-agents build
ai-agents install
ai-agents init-opencode
```

Suggested layout:

```text
go.mod
main.go
internal/
  app/
  build/
  install/
  platforms/
  prompts/
  files/
```

### Core Design

1. `prompts`
   - Parse prompt markdown files into a typed internal model.
   - Split frontmatter from body.
   - Resolve `{{include:file.md}}` directives.
   - Load `source/model-mappings.json`.

2. `platforms`
   - Define platform descriptors for Claude, OpenCode, and later Codex.
   - Each descriptor declares output paths, supported artifact kinds, base instruction filename, and rendering rules.

3. `build`
   - Walk `source/prompts/`.
   - Convert each prompt into one or more platform artifacts.
   - Copy shared base instructions and skills into `build/`.
   - Emit warnings such as unmapped models.

4. `install`
   - Copy built artifacts into target config directories.
   - Handle overwrite prompts or force mode.
   - Print concise install summaries.

5. `app`
   - Own CLI parsing, help output, shared flags, and command dispatch.

## Key Refactor Principle

Do not port the shell scripts line-for-line.

The main win comes from turning the system into:

- typed input model
- renderer per platform
- generic installer per platform descriptor

If the Go version mirrors the shell branches one-to-one, it will not be worth it.

## Functional Requirements To Preserve

### Build

- `--work` mode behavior for model remapping.
- `--chatgpt-provider` selection and validation.
- GPT provider normalization for non-work OpenCode builds.
- generation of Claude agents and commands
- generation of OpenCode agents, commands, and modes
- copying `AGENTS.md` into platform-specific base instruction files
- copying skills to both output trees
- writing `build/.unmapped-models`
- final build summary output

### Install

- install Claude only, OpenCode only, or both
- interactive target selection when no target is specified
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
- print configuration summary

## Unknowns / Decisions To Validate Early

### 1. Frontmatter parsing

Options:
- Use a YAML package.
- Parse the limited frontmatter shape in-house.

Recommendation:
- Start by evaluating whether a small, reputable YAML package is acceptable.
- If keeping dependencies to zero is more important, implement a constrained parser only for the frontmatter patterns already used in this repo.

### 2. Wrapper strategy

Options:
- Replace shell scripts immediately.
- Keep thin `build.sh` / `install.sh` / `opencode-init.sh` wrappers that call the Go binary.

Recommendation:
- Keep wrappers during migration so existing README commands still work.

### 3. Output compatibility

Recommendation:
- Treat `build/` diffs against the current shell implementation as the main acceptance gate.

## Proposed Implementation Phases

### Phase 1: Model and Build Prototype

- Create Go module and CLI skeleton.
- Implement prompt discovery, frontmatter/body split, include expansion, and model mapping load.
- Implement `build` for Claude and OpenCode only.
- Compare generated `build/` output against current shell output.

Deliverable:
- A Go build command that can reproduce the existing generated files closely enough for diff-based review.

### Phase 2: Generic Installer

- Implement install target descriptors.
- Implement copy-with-overwrite logic.
- Implement interactive and force flows.
- Reproduce `install.sh` behavior for Claude and OpenCode.

Deliverable:
- `ai-agents install` supports the current install matrix.

### Phase 3: OpenCode Init

- Implement `init-opencode` as a thin shared installer use case.
- Reproduce current config copy UX.

Deliverable:
- `ai-agents init-opencode` replaces `opencode-init.sh` behavior.

### Phase 4: Compatibility Wrappers

- Convert existing shell scripts into thin wrappers around the Go binary or a `go run` entrypoint.
- Preserve current flags and help output as much as practical.

Deliverable:
- Existing documented commands keep working.

### Phase 5: Codex Support

- Add a Codex platform descriptor and renderer.
- Reuse the build and install engines instead of duplicating any flow.

Deliverable:
- Third platform added with minimal core changes.

## Testing and Verification Plan

### Build Verification

- Run current shell build and capture output tree.
- Run Go build and capture output tree.
- Diff:
  - file presence
  - frontmatter fields
  - prompt body content
  - skill/base instruction copies
  - unmapped model warnings

### Install Verification

- Test install for:
  - Claude only
  - OpenCode only
  - both
  - `--skip-build`
  - `--work`
  - each ChatGPT provider option
  - interactive prompt paths
  - force overwrite mode

### Regression Checks

- Confirm README examples still map to valid commands.
- Confirm build output paths stay stable.
- Confirm no user config files are overwritten without prompt unless forced.

## Risks

### Medium Risk

- YAML/frontmatter parsing differs subtly from current `yq` behavior.
- Output formatting changes create noisy diffs even when logically correct.
- Interactive install UX may drift from current behavior.

### Low Risk

- Generic copy logic is simpler and safer in Go than shell.
- Platform descriptor design should reduce future risk once established.

## Why Go Instead of More Shell

- Better fit for typed platform descriptors and shared rendering/install logic
- easier diff-based tests and unit tests
- easier to add Codex without tripling branch logic
- clearer separation between parsing, rendering, and installing
- less reliance on fragile text pipelines

## Why This Could Still Fail

It will fail if the rewrite focuses on syntax replacement instead of architecture.

Bad outcome:
- one giant `main.go` that reimplements the shell scripts directly

Good outcome:
- small command layer
- typed internal model
- renderer per platform
- generic installer

## Recommended First Slice

Before replacing anything, build only this thin vertical slice:

1. parse prompts
2. render Claude + OpenCode output into a temporary build directory
3. diff against the current shell build output

If that slice is not materially simpler than the shell version, stop there.

## Branch and Execution Notes

- Working branch: `go-refactor-experiment`
- Requested constraint: planning only for now; no implementation changes yet
- Suggested next step after approval: implement Phase 1 only and evaluate complexity before touching install
