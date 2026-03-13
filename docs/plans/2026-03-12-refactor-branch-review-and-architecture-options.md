# Refactor Branch Review And Architecture Options

Date: 2026-03-12

## Goal

Review the two refactor branches against `main`, identify the strongest ideas from each, and outline a better third-path architecture.

## Branches Reviewed

- `main` - reference standard for current behavior and user workflow
- `go-refactor-experiment`
- `refactor/python-build-system`

## Executive Recommendation

`main` remains the correctness baseline.

Of the two refactor branches, `go-refactor-experiment` is the stronger continuation path because it preserves more behavior, adds meaningful test coverage, and improves internal structure without discarding the current CLI workflow.

The Python branch has strong ideas around simplicity and declarative configuration, but it regresses important behavior and safety guarantees. Its ideas should be reused, but the branch should not be merged as-is.

If maintainer fluency is a major factor and Python is the dominant strength, a new Python-based third branch is reasonable, but it should be built with stronger modular boundaries and parity tests than the current Python refactor branch.

## Scorecard

Scale: `5` = at or above `main`, `3` = acceptable but weaker, `1` = significant regression.

| Category | `main` | `go-refactor-experiment` | `refactor/python-build-system` |
|---|---:|---:|---:|
| Feature parity | 5 | 4 | 2 |
| User workflow compatibility | 5 | 3 | 2 |
| Maintainability | 3 | 5 | 4 |
| Test coverage | 2 | 5 | 1 |
| Install safety | 4 | 4 | 2 |
| Build system clarity | 3 | 4 | 5 |
| Documentation accuracy | 4 | 3 | 2 |
| Merge readiness | 5 | 3 | 1 |

## Key Findings

### `go-refactor-experiment`

Strengths:

- Clear package boundaries for CLI dispatch, build orchestration, prompt loading, install logic, and filesystem operations
- Good test coverage for build helpers, install overwrite flows, prompt include handling, and CLI help
- Preserves the existing shell entrypoints while introducing a stronger internal CLI design

Main gaps:

- Wrapper scripts are not fully compatible when run from outside the repository because parts of the Go CLI still resolve paths from the current working directory rather than the repository root
- README claims and actual runtime behavior still need reconciliation in a few places
- End-to-end parity tests against generated output are still missing

### `refactor/python-build-system`

Strengths:

- The build system is easier to read at a glance
- The harness definition approach is simple and attractive
- Python 3.11 standard library tooling reduces dependency friction compared with `yq` and `jq`

Main gaps:

- OpenCode modes lose parity because generated files do not include `mode: primary`
- `--chatgpt-provider` behavior from `main` is missing
- Install behavior is less safe because overwrite handling is weaker
- There is no meaningful automated test coverage

## Third-Path Design Principles

Any new implementation should follow these rules:

1. `main` defines behavioral compatibility
2. generated output is locked down with golden tests
3. wrapper scripts must work regardless of current working directory
4. install flows must preserve explicit overwrite protection
5. documentation must describe actual CLI behavior, not intended behavior
6. renderer configuration should be declarative and easy to extend

## Behavioral Contract To Preserve

The third branch should treat these behaviors as required unless there is an explicit decision to change them:

### Commands

- `build` generates Claude and OpenCode artifacts from `source/prompts/` and copies shared skills and base instructions
- `install` can install Claude only, OpenCode only, or both
- `init-opencode` installs `source/opencode.json` into the user's OpenCode config directory with overwrite confirmation

### Build flags

- `--work` switches model selection to `source/model-mappings.json`
- `--chatgpt-provider` rewrites GPT-family OpenCode models for non-work builds
- build output lands in `build/` by default

### Install guarantees

- overwrite prompts must remain explicit unless the user passes a force flag
- `--skip-build` must reuse the current build directory without silently changing its contents
- OpenCode config installation must remain opt-in and should not overwrite customized config without confirmation

### Output structure

- Claude output:
  - `build/claude/agents/*.md`
  - `build/claude/commands/*.md`
  - `build/claude/skills/*`
  - `build/claude/CLAUDE.md`
- OpenCode output:
  - `build/opencode/agent/*.md`
  - `build/opencode/command/*.md`
  - `build/opencode/skill/*`
  - `build/opencode/AGENTS.md`
- modes must render with the correct OpenCode metadata, including `mode: primary`

## Shared Domain Model

Regardless of implementation language, the core logic should be based on a small explicit domain model.

### Core entities

- `PromptDoc`
  - `name`
  - `description`
  - `type` (`subagent`, `command`, `mode`)
  - `body`
  - `claude_config`
  - `opencode_config`
  - `source_path`
- `HarnessSpec`
  - harness name
  - output directories
  - base instructions filename
  - install target path
- `BuildOptions`
  - repo root
  - output dir
  - work mode flag
  - ChatGPT provider
  - optional selected harnesses
- `InstallOptions`
  - repo root
  - build dir
  - home dir
  - target selection
  - force flag
  - skip-build flag

### Pipeline stages

1. locate repo root
2. load prompt files
3. parse frontmatter
4. expand includes
5. validate prompt metadata
6. apply provider selection and work mappings
7. render harness-specific frontmatter and content
8. write artifacts
9. copy base instructions and skills
10. optionally install to user config locations

Keeping these stages explicit matters more than the language choice. Most regressions in the reviewed branches came from stage drift, not from syntax.

## Python Architecture Option

Recommended when the primary maintainer is substantially more fluent in Python.

### Proposed layout

```text
ai_agents/
  cli.py
  repo.py
  models.py
  fs.py
  build/
    service.py
  install/
    service.py
  prompts/
    parser.py
    includes.py
    mappings.py
    loader.py
  render/
    harnesses.py
    claude.py
    opencode.py
tests/
  test_parser.py
  test_mappings.py
  test_render_golden.py
  test_install.py
  test_wrappers.py
```

### Responsibilities

- `cli.py` - `build`, `install`, and `init-opencode` commands
- `repo.py` - repository root discovery based on script location and explicit path passing
- `models.py` - typed dataclasses for prompts, harnesses, and command options
- `prompts/*` - frontmatter parsing, include expansion, model selection, and validation
- `render/*` - harness-specific artifact generation with explicit OpenCode mode handling
- `build/service.py` - orchestrates load, transform, render, and write
- `install/service.py` - interactive overwrite flow and safe installation behavior
- `fs.py` - atomic-ish writes, copy helpers, reset helpers, and directory utilities

### Suggested internal APIs

- `repo.find_repo_root(start: Path | None = None) -> Path`
- `loader.load_prompts(prompts_dir: Path) -> list[PromptDoc]`
- `mappings.select_model(model: str, provider: str, work_mode: bool, mapping_table: dict[str, str]) -> tuple[str, bool]`
- `render_claude(doc: PromptDoc) -> Artifact | None`
- `render_opencode(doc: PromptDoc, selected_model: str) -> Artifact | None`
- `build_project(opts: BuildOptions) -> BuildReport`
- `install_targets(opts: InstallOptions) -> InstallReport`

### Python implementation notes

- Use `argparse` for command shape parity and predictable help output
- Use `dataclasses` and `Enum` to avoid loose dict-heavy code
- Keep rendering pure: functions should take `PromptDoc` plus options and return artifacts, not write files directly
- Use fixture directories for golden output tests so behavior changes are obvious in diffs
- If TOML or YAML support changes in the future, isolate that behind the parser module so renderer and install code stay untouched

### Why this Python option is viable

- The repository is dominated by text transformation and file generation, which Python handles well
- Readability is likely highest for a Python-fluent maintainer
- Maintainability can be strong if the code is modular and guarded by parity tests

### Python risks to avoid

- do not collapse the system into one script
- do not weaken overwrite prompts
- do not change frontmatter and behavior at the same time without regression tests

## Go Architecture Option

Recommended when long-term compiled CLI stability and stronger package boundaries matter more than maintainer familiarity.

### Proposed layout

```text
cmd/ai-agents/
  main.go
internal/
  cli/
  repo/
  domain/
  prompts/
  render/
  platforms/
    claude/
    opencode/
  buildsys/
  install/
  files/
  testdata/
```

### Responsibilities

- `internal/cli` - command parsing, help, and dispatch
- `internal/repo` - repository root detection independent of `cwd`
- `internal/domain` - core types and option structs
- `internal/prompts` - frontmatter parsing, include expansion, model mapping, validation
- `internal/platforms/*` - target-specific rendering
- `internal/buildsys` - orchestration layer for load, transform, render, and write
- `internal/install` - overwrite prompting, installation, and `opencode.json` initialization
- `internal/files` - filesystem helpers and copy primitives

### Suggested internal APIs

- `repo.Root() (string, error)` or `repo.Find(start string) (string, error)`
- `prompts.LoadAll(dir string) ([]PromptDoc, error)`
- `prompts.ResolveModel(model string, provider string, workMode bool, mappings ModelMappings) (string, bool)`
- `platforms.ClaudeArtifact(doc PromptDoc) (*Artifact, error)`
- `platforms.OpenCodeArtifact(doc PromptDoc, model string) (*Artifact, error)`
- `buildsys.Run(opts Options) error`
- `install.Run(opts Options) error`

### Go implementation notes

- Use concrete structs rather than deeply nested `map[string]any` beyond the parsing boundary
- Keep repo-root detection in one package and pass resolved paths through options instead of re-reading `cwd`
- Keep command handlers thin; all meaningful logic should live below the CLI layer
- Prefer package seams that reflect the pipeline stages rather than creating interfaces preemptively
- Golden tests should exercise the public orchestration layer, not only unit helpers

### Why this Go option is viable

- Strong package boundaries fit a growing CLI well
- Static typing helps when renderer and install logic become more interconnected
- A compiled CLI can become the stable long-term interface

### Go risks to avoid

- do not overcomplicate a text-processing tool with needless abstractions
- do not let path handling depend on `cwd`
- do not treat package structure as a substitute for end-to-end parity tests

## Recommendation By Maintainer Context

### If Python is the maintainer's stronger language

Build the third branch in Python, but use Go-style architectural discipline:

- multiple modules
- explicit domain types
- parity tests before behavioral changes
- safe install semantics matching `main`

### If long-term CLI robustness is the top priority

Continue from the Go refactor branch, then simplify its renderer and configuration model using the best ideas from the Python branch.

## Migration Plan

The third branch should be implemented in phases so parity is proven before cleanup work expands scope.

### Phase 1 - lock the contract

- capture sample output from `main` for representative prompts, commands, and modes
- define golden fixtures for Claude and OpenCode artifacts
- document exact command help text and expected overwrite prompts
- record current behavior for `--work`, `--chatgpt-provider`, and `--skip-build`

Exit criteria:

- fixtures exist for all current prompt types
- expected output tree is checked into tests or fixtures
- behavior differences from `main` are explicitly documented

### Phase 2 - build the new core pipeline

- implement repo-root discovery independent of `cwd`
- implement prompt loading, include expansion, and model selection
- implement Claude and OpenCode renderers
- generate build output identical or intentionally equivalent to `main`

Exit criteria:

- golden output tests pass
- mode generation parity is explicitly verified
- provider selection and work mapping tests pass

### Phase 3 - build install and wrapper compatibility

- implement install target selection
- implement overwrite prompts and force behavior
- implement `init-opencode`
- convert shell wrappers into strict pass-through compatibility shims

Exit criteria:

- wrapper tests pass from repo root and non-repo directories
- install overwrite tests pass for accept, decline, and force cases
- `opencode.json` remains opt-in

### Phase 4 - simplify and document

- remove duplicated or transitional code
- update README examples to match actual behavior
- add extension notes for future harness support

Exit criteria:

- README examples are verified against command help output
- architecture doc and contribution notes are current
- no undocumented behavioral drift remains

## Test Strategy

The third branch should have both narrow unit tests and broad behavioral tests.

### Unit tests

- frontmatter parsing
- include expansion, including cycle detection
- model provider selection
- work mapping behavior
- harness-specific metadata rendering

### Golden tests

- full build output for a representative prompt set
- OpenCode mode files with `mode: primary`
- command artifacts and agent artifacts for both harnesses
- base instructions and skill copying

### Behavioral integration tests

- `build` from repo root
- `build` from outside repo root via wrapper
- `install --skip-build`
- `install --work`
- `install --chatgpt-provider <provider>`
- `init-opencode` overwrite decline and confirm flows

### Documentation verification

- help output snapshot tests for all commands
- README command examples exercised by tests where practical
- explicit assertions that documented flags exist and behave as described

## Decision Framework

Choose the implementation language using these criteria, in this order:

1. maintainer fluency
2. likelihood of preserving behavioral parity quickly
3. testability of the implementation
4. expected contributor pool
5. appetite for a compiled long-term CLI

Under that framework:

- choose Python if maintainer velocity and readability dominate
- choose Go if long-term compiled CLI stability and broader package-scale refactoring dominate
- in either case, reject the design if it weakens parity or safety to gain aesthetic simplicity

## Minimum Acceptance Criteria For Any Third Branch

- golden tests for generated Claude and OpenCode output
- explicit tests for OpenCode mode generation
- explicit tests for `--chatgpt-provider`
- explicit tests for `--work` model mapping
- wrapper tests executed from outside the repo root
- overwrite prompt tests for install flows
- README validation against actual command behavior

## Final Recommendation

Today, the best available branch to continue is `go-refactor-experiment`.

If maintainer fluency is the deciding factor, a new Python branch is a valid choice and may be the better one, but only if it is rebuilt around parity-first testing and safer install behavior. The current Python refactor branch is not sufficient as the base.
