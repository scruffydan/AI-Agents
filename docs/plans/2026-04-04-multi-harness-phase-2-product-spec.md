# Multi-Harness Phase 2 Product Spec

Date: 2026-04-04

## Summary

This branch establishes a Python-based packaging system that compiles a shared prompt and skill source tree into harness-specific outputs for `opencode`, `claude`, and `codex`.

It replaces shell-centric build logic with a structured Python CLI and domain model that supports build, install, lint, listing, model-profile resolution, and verification workflows.

This spec is intended as a handoff document for a future AI agent that will continue the work from this branch. The next phase should treat the Python pipeline in this branch as the system of record and improve its correctness, safety, and operator experience rather than introducing a new orchestration model.

## Product Intent

The product should let maintainers author prompts once in a harness-neutral format, then reliably generate, validate, inspect, and install harness-specific artifacts across multiple AI coding environments.

The platform should be:

- safe for local use
- deterministic in CI
- easy to inspect when something fails
- straightforward to extend with new harnesses, profiles, and validation rules

## Current Baseline

This branch already provides all of the following:

- a Python CLI entrypoint via `ai-agents`
- shared source parsing from `source/prompts` and `source/skills`
- harness registries for `opencode`, `claude`, and `codex`
- harness-specific rendering from a common source model
- build output generation with a machine-readable manifest
- install planning with `--dry-run`
- model profile resolution by environment
- OpenCode provider override support
- a `doctor` command for source, build, and installed-state checks
- automated tests for parsing, rendering, build, install, and filesystem safety guards

## Problem Statement

The branch has completed the main architectural transition to Python, but the operational contract is not yet fully trustworthy.

The next phase should focus on making the CLI behavior align with operator expectations in real workflows:

- filesystem boundaries must be enforced consistently
- install success must mean something was actually installable
- verification must reflect selected or actual outputs, not idealized global state
- custom build locations must remain first-class

This phase is not about adding more harnesses or more prompt content. It is about making the existing system dependable enough to serve as the canonical packaging pipeline.

## Primary Goals

1. Make the Python pipeline the canonical build and install path.
2. Preserve one-source authoring across all supported harnesses.
3. Guarantee filesystem-safe build and install behavior.
4. Make install and verification trustworthy for both humans and automation.
5. Support future harness additions with minimal new branch-specific logic.

## Non-Goals

- replacing the source document format again
- adding new harnesses in this phase
- building a GUI or web dashboard
- supporting arbitrary user-authored plugins
- preserving old shell scripts as first-class workflows
- introducing a new framework or dependency-heavy orchestration layer

## Target Users

### 1. Repository Maintainers

They maintain prompt and skill definitions in `source/` and need confidence that generated outputs stay correct across harnesses.

### 2. Developers Installing Local Config

They want predictable install behavior into their local agent configuration directories, including partial installs and dry runs.

### 3. CI and Automation

CI needs deterministic commands, machine-readable output where useful, and reliable exit codes.

### 4. Future AI Agents and Contributors

They need clear extension points for harnesses, profiles, manifests, and verification behavior without reverse-engineering branch-specific assumptions.

## Core User Stories

- As a maintainer, I can define prompts once and build outputs for one or more harnesses.
- As a maintainer, I can inspect what was generated and where it came from.
- As a developer, I can install only selected harnesses or components.
- As a developer, I can run a dry run before overwriting local config.
- As a CI workflow, I can fail fast when source content, build outputs, or install expectations are invalid.
- As a future contributor, I can add a harness or profile without rewriting the core pipeline.

## Functional Requirements

### Source and Validation

- The system must parse shared source documents from `source/prompts` and `source/skills`.
- The system must validate document frontmatter, harness targeting, and allowed metadata keys before rendering.
- The system must reject unsafe local-file behavior including symlink-based prompt loading and unsafe include traversal.

### Build

- The system must build one or more selected harnesses from the shared source model.
- The system must resolve model settings from named profiles and named environments.
- The system must emit harness-specific artifacts in deterministic paths.
- The system must emit a machine-readable manifest describing generated artifacts and their source paths.

### Install

- The system must support install by selected harness.
- The system must support install by selected component such as `base`, `documents`, and `skills`.
- The system must support `--dry-run` without filesystem mutation.
- The system must clearly differentiate between a valid install plan and an invalid or incomplete one.

### Verification

- The system must provide a `doctor` workflow for source, build, and optional installed-state checks.
- The system must support both human-readable and JSON output for verification.
- The system must use exit codes that match real operational success or failure.

## Reliability Requirements

- Build output paths must always stay within the allowed build root.
- Install must not silently succeed when required build artifacts are missing.
- Verification must reflect what was actually built or installed, not assume every harness is present.
- Verification must support non-default build output locations.
- Generated output should remain deterministic across repeated runs from identical source.

## Security Requirements

- Source loading must reject symlinked prompt trees.
- Include expansion must remain confined to the declared include root.
- Install and build paths must be boundary-checked before writes occur.
- Replacement logic must continue to reject symlink targets during file and tree replacement.
- The core packaging workflow must not depend on ambient shell behavior for correctness.

## UX and CLI Requirements

- `build` should clearly report selected harnesses, environment, output location, and artifact counts.
- `install` should clearly report planned actions, installed targets, and actionable failures.
- `doctor` should distinguish warnings from failures and be reliable in CI.
- Exit codes must align with actual outcome semantics.

Success semantics:

- `0` only for successful operations
- non-zero for invalid source, invalid build state, or failed install preconditions

## Product Decisions Locked By This Spec

These decisions should be treated as fixed unless a later plan intentionally changes them.

1. `source/` remains the only semantic source of truth.
2. Generated harness output remains disposable build output.
3. The Python CLI remains the canonical workflow.
4. OpenCode remains the default harness unless intentionally changed later.
5. No third-party Python dependency should be added for this phase.
6. No new harness is added in this phase.
7. Future behavior should extend manifest- and metadata-driven flows rather than adding parallel special cases.

## Known Gaps To Address Next

The next AI agent should treat these as priority correctness issues:

1. Output-dir confinement should reject out-of-tree paths even when the target path does not yet exist.
2. `install --skip-build` should fail when planned sources are missing instead of returning a misleading success.
3. `doctor --installed` should validate selected or manifest-backed installs rather than assuming every harness is installed.
4. `doctor` should support custom build output directories instead of assuming `build/manifest.json`.
5. Regression tests should be added for all of the above.

## Recommended Next Milestone

The next milestone should focus on operational correctness, not feature expansion.

Deliverables:

- hardened path validation for build output
- trustworthy install failure semantics
- manifest-aware or selection-aware doctor behavior
- custom build output support in verification
- regression tests covering each corrected behavior
- small CLI output improvements only where they improve operator clarity

## Acceptance Criteria

This phase is complete when all of the following are true:

- building outside the repo build root is rejected even if the target path does not yet exist
- a skip-build install with missing artifacts exits non-zero and explains what is missing
- `doctor --installed` passes after a valid default install
- `doctor` can validate builds created in custom output directories
- existing tests still pass
- new regression tests cover the four corrected behaviors above

## Implementation Guidance For A Future AI Agent

- Keep the current Python package structure.
- Prefer minimal changes over architectural churn.
- Extend manifest-driven behavior rather than introducing a second source of truth.
- Add failing tests before changing behavior.
- Preserve harness-neutral source authoring.
- Do not reintroduce shell-script orchestration as the primary path.
- Treat CLI success and failure semantics as part of the product contract, not just implementation details.

## Suggested Verification Commands

The next AI agent should expect to use commands in this shape while working:

- `python3 -m unittest`
- `python3 -m unittest tests.test_build_service tests.test_install tests.test_doctor tests.test_cli`
- `python3 -m ai_agents build`
- `python3 -m ai_agents install --dry-run`
- `python3 -m ai_agents doctor --json`

## Handoff Summary

This branch is already a strong architectural base.

The remaining work is not another refactor. It is the tightening pass that makes the new Python pipeline safe to rely on as the canonical build, install, and verification system for multi-harness AI agent packaging.
