# Multi-Harness Phase 2 Agent Prompt

Date: 2026-04-04

Use this prompt to hand off the current branch to another AI agent.

## Prompt

You are continuing work on the `refactor/multi-harness-core` branch of the `AI-Agents` repository.

This branch has already completed the main migration from shell-driven build logic to a Python packaging pipeline. Treat the Python system in this branch as the canonical implementation. Do not reintroduce shell-script orchestration as the primary workflow.

### Current Architecture

The repo now has:

- a Python CLI entrypoint in `ai_agents/cli.py`
- shared source documents in `source/prompts` and `source/skills`
- harness registries for `opencode`, `claude`, and `codex`
- rendering logic in `ai_agents/render/`
- build orchestration in `ai_agents/build/service.py`
- install planning and execution in `ai_agents/install/service.py`
- model profile resolution in `ai_agents/profiles/resolver.py`
- verification in `ai_agents/doctor.py`
- automated tests under `tests/`

The product intent is to let maintainers author prompts once in a harness-neutral format and then build, validate, inspect, and install harness-specific outputs reliably.

### Your Goal

Improve operational correctness and trustworthiness without changing the overall architecture.

Do not add new harnesses. Do not redesign the source document model. Do not add third-party Python dependencies unless absolutely necessary.

### Priority Issues To Fix

1. Build output path confinement is incomplete.
The build pipeline should reject output paths outside the repo `build/` root even when the requested path does not yet exist.

2. `install --skip-build` can report success when build artifacts are missing.
This should fail clearly with a non-zero exit path and actionable messaging.

3. `doctor --installed` assumes all harnesses are installed.
It should instead verify only relevant installed targets, based on actual build or install context.

4. `doctor` assumes the manifest always lives at `build/manifest.json`.
It should support custom build output directories.

### Product Constraints

- keep `source/` as the only semantic source of truth
- keep generated output disposable
- preserve OpenCode as the default harness
- keep the Python CLI as the canonical workflow
- prefer manifest-driven or metadata-driven behavior over hard-coded special cases
- make minimal, local changes rather than broad refactors

### Required Outcomes

Your implementation is successful when all of the following are true:

- building outside the repo build root is rejected, even for nonexistent target paths
- `install --skip-build` fails when required artifacts are missing
- `doctor --installed` passes after a valid default install
- `doctor` can validate builds created in custom output directories
- regression tests cover each corrected behavior
- existing tests continue to pass

### Implementation Guidance

- start by reading the current implementation and tests
- add failing tests before changing behavior
- preserve current package structure
- prefer the smallest correct changes
- keep CLI success and failure semantics explicit and reliable
- update tests and any user-facing docs if command behavior changes

### Useful Files

- `ai_agents/cli.py`
- `ai_agents/build/service.py`
- `ai_agents/install/service.py`
- `ai_agents/doctor.py`
- `ai_agents/domain/harnesses.py`
- `ai_agents/domain/options.py`
- `ai_agents/domain/manifest.py`
- `tests/test_build_service.py`
- `tests/test_install.py`
- `tests/test_doctor.py`
- `tests/test_cli.py`
- `tests/test_security_guards.py`

### Suggested Verification Commands

- `python3 -m unittest`
- `python3 -m unittest tests.test_build_service tests.test_install tests.test_doctor tests.test_cli`
- `python3 -m ai_agents build`
- `python3 -m ai_agents install --dry-run`
- `python3 -m ai_agents doctor --json`

### Deliverable

Implement the fixes, add regression coverage, and leave the branch in a state where the Python pipeline is a dependable canonical build, install, and verification system for all currently supported harnesses.
