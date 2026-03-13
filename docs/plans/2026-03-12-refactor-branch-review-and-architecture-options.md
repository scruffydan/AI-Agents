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
