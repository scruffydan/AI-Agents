# Compatibility and Verification Plan

Date: 2026-03-29

## Goal

Strengthen AI-Agents as a canonical-source, multi-harness generator by adding better compatibility contracts, machine-readable build metadata, safer install planning, and a `doctor` command.

This plan builds on the completed multi-harness refactor and focuses on reliability, inspectability, and operator experience rather than adding more orchestration features.

## Why This Work Matters

The current architecture is already good at rendering one source tree into OpenCode, Claude, and Codex outputs.

What it lacks is the next layer of maturity:

- a fuller compatibility contract for each harness
- a stable manifest describing what was generated
- safer and more inspectable install planning
- one command that can explain whether the repo, build output, and installed state are healthy

Projects like `everything-claude-code`, `oh-my-openagent`, and `oh-my-claudecode` suggest that the highest-leverage improvements are not more agents. They are better adapters, better verification, and better operator visibility.

## Product Decisions

These decisions should be treated as locked for this work unless a later plan intentionally changes them.

1. `source/` remains the only semantic source of truth
2. generated harness output remains disposable build output
3. OpenCode stays the default harness
4. no third-party Python dependencies are added
5. no hook-heavy orchestration framework is introduced
6. no new harness is added as part of this plan
7. compatibility is modeled as data before new behavior is added
8. install and doctor features must remain safe and non-destructive by default

## Success Criteria

This work is successful when all of the following are true:

- harness behavior is described through a richer compatibility contract instead of scattered assumptions
- `build` emits a manifest that describes generated artifacts in a stable format
- `install --dry-run` shows what would happen without mutating the filesystem
- install can target logical components such as base files, rendered documents, and skills
- `python3 -m ai_agents doctor` can detect common source, build, and install problems with clear output and non-zero failure status
- tests cover manifest generation, install planning, dry-run behavior, selective install behavior, and doctor checks
- docs explain the new verification and install workflows clearly

## Non-Goals

- adding agent-team or workflow orchestration features
- building a plugin marketplace or harness package manager
- implementing incremental build caching
- supporting every harness convention in the ecosystem
- preserving undocumented behavior if a cleaner compatibility contract is better

## Design Principles

### 1. Reuse behavior, not files

Shared semantics should stay in Python domain models and source documents. Harness outputs should remain thin render targets.

### 2. Make compatibility explicit

If the build or install pipeline depends on a harness rule, that rule should live in harness metadata rather than in a hard-coded branch somewhere else.

### 3. Prefer inspection over magic

Operators should be able to answer:

- what was generated?
- where will it install?
- what changed?
- what is broken?

without reading Python code.

### 4. Keep the architecture small

Borrow the best ideas from larger systems, but stop before they become framework overhead.

## Current Gaps

The current codebase already has a strong harness registry in `ai_agents/domain/harnesses.py`, a clean build pipeline in `ai_agents/build/service.py`, and shared model intent in `source/model-profiles.toml`.

The main gaps are:

- harness metadata does not yet describe install or output behavior at a component level
- build output is inspectable only by walking the filesystem
- install behavior is safe, but not yet plan-driven or dry-run friendly
- there is no single verification command for source, build output, and installed state
- tests validate behavior, but do not yet treat the generated output shape as a first-class contract

## Proposed Architecture

### A. Expand the Harness Compatibility Contract

Extend `HarnessSpec` so it describes not only output layout and supported metadata keys, but also compatibility-relevant structure.

Recommended additions:

- `components`: logical output/install groups such as `base`, `documents`, `skills`
- `install_components`: mapping from component names to install entries
- `legacy_paths`: optional compatibility aliases or known historical locations
- `notes`: optional human-readable compatibility notes for doctor output

This should make the harness registry the source of truth for:

- what kinds of artifacts a harness expects
- which parts are installable independently
- which paths are expected during install verification
- what compatibility compromises exist for a harness

The build, install, and doctor layers should consume this contract instead of adding new harness-specific branches.

### B. Add a Build Manifest

Each build should emit a manifest file, likely `build/manifest.json`.

The manifest should include:

- schema version
- repo root and build root
- build environment
- selected harnesses
- source document records
- rendered artifact records
- copied skill records
- copied base file records
- install component labels where relevant

Each artifact record should be able to answer:

- source file path
- harness
- document kind
- model profile
- relative output path
- logical component (`documents`, `skills`, `base`)

This manifest should become the common contract used by:

- install planning
- doctor checks
- test assertions
- future diff or audit tooling

### C. Introduce an Install Plan Layer

The install system should stop reasoning directly from build directories and start reasoning from a typed install plan.

Recommended model:

- `InstallPlan`
- `InstallAction`
- `InstallConflict`

An install plan should be created before any filesystem mutation happens.

It should support:

- full install
- harness-filtered install
- component-filtered install
- dry-run preview

Each action should include:

- source path
- destination path
- component
- harness
- action type (`replace_tree`, `replace_file`, `skip`, `prompt`)
- overwrite/conflict state

The current safe replace behavior should remain, but it should execute from this plan instead of deriving behavior ad hoc.

### D. Add a Doctor Command

Add `python3 -m ai_agents doctor` as a non-destructive verification command.

The first version should check four layers.

#### Source checks

- required directories exist
- prompt files parse successfully
- model profiles load successfully
- harness registry is internally consistent
- unsupported metadata keys are reported cleanly

#### Build checks

- manifest exists when expected
- manifest schema is valid
- manifest references existing artifacts
- no duplicate output path collisions exist
- selected harness outputs match the manifest

#### Install checks

- expected install destinations can be derived from the harness contract
- optionally verify installed paths exist with `doctor --installed`
- warn, not fail, when optional install targets are absent unless installed verification is explicitly requested

#### UX checks

- provide human-readable output by default
- provide `--json` for machine-readable output
- exit non-zero on real failures

Doctor should explain problems clearly and point to the relevant file or path.

## CLI Changes

The command surface should stay small.

### New or expanded commands

```text
python3 -m ai_agents build [--harness <name> ...] [--all] [--work] [--output <dir>]
python3 -m ai_agents install [--harness <name> ...] [--all] [--work] [--skip-build] [--force] [--dry-run] [--component <name> ...]
python3 -m ai_agents doctor [--installed] [--json]
```

### Command behavior notes

- `install --dry-run` must not write, delete, or chmod anything
- `install --component` must filter by logical compatibility contract components
- `doctor --installed` should verify the installed view, not just the repo/build view
- `doctor --json` should expose enough structure for future tooling and tests

## Recommended File Changes

### Domain and compatibility

- `ai_agents/domain/harnesses.py`
- possibly a new `ai_agents/domain/manifest.py`
- possibly a new `ai_agents/domain/install_plan.py`

### Build pipeline

- `ai_agents/build/service.py`
- possibly a new `ai_agents/build/manifest.py`

### Install pipeline

- `ai_agents/install/service.py`

### Verification

- likely new `ai_agents/doctor.py` or `ai_agents/verify/service.py`
- `ai_agents/cli.py`

### Tests

- new tests for manifest generation
- new tests for install planning and dry-run
- new tests for doctor

### Docs

- `README.md`
- optional additional architecture note in `docs/`

## Phased Implementation Plan

### Phase 1 - Compatibility Contract

Implement the richer harness metadata model first.

Tasks:

- extend `HarnessSpec` with logical components and compatibility notes
- move any remaining output/install assumptions behind that contract
- update tests that rely on older harness assumptions

Exit criteria:

- build and install both derive component behavior from the harness registry
- no new hard-coded harness branches are introduced to support later phases

### Phase 2 - Build Manifest

Implement stable manifest generation during build.

Tasks:

- define manifest schema and version
- emit manifest on successful build
- make manifest records deterministic for stable tests
- add tests for manifest shape and path correctness

Exit criteria:

- successful builds emit `manifest.json`
- tests can assert output shape from the manifest instead of brittle file counts

### Phase 3 - Install Planning and Dry-Run

Add a typed planning step before install mutation.

Tasks:

- create install plan and action models
- generate plans from build output plus harness contract
- add `--dry-run`
- add component filtering
- keep existing symlink and replace safety behavior

Exit criteria:

- dry-run emits a plan and makes no filesystem changes
- selective install works for `base`, `documents`, and `skills`

### Phase 4 - Doctor Command

Implement non-destructive verification.

Tasks:

- add source/build/install checks
- add clear human-readable summaries
- add `--json`
- add `--installed`
- document exit behavior

Exit criteria:

- doctor can catch representative broken states in tests
- doctor output is useful without reading source code

### Phase 5 - Tests and Docs Polish

Finalize the operator experience.

Tasks:

- convert remaining brittle tests to manifest- or contract-based assertions
- document build manifest, dry-run, component install, and doctor
- add examples to README

Exit criteria:

- docs match actual CLI behavior
- verification commands cover the new features

## Verification Strategy

Every phase should keep the existing baseline checks green:

```bash
python3 -m unittest discover -s tests
python3 -m ai_agents lint
python3 -m ai_agents build --all --work
```

Additional phase-specific checks should be added as work lands.

### Compatibility contract checks

- harness registry unit tests
- component mapping tests

### Manifest checks

- schema shape tests
- artifact-to-source mapping tests
- deterministic ordering tests

### Install plan checks

- dry-run no-op tests
- selective component tests
- conflict classification tests

### Doctor checks

- broken source fixture tests
- broken manifest fixture tests
- missing install target tests
- JSON output snapshot or structured assertion tests

## Risks and Mitigations

### Risk: Contract over-design

Mitigation:

- start with only the components and notes needed for current harnesses
- avoid modeling hypothetical future harnesses too early

### Risk: Manifest becomes a second source of truth

Mitigation:

- generate manifest only from the already-resolved build pipeline
- never hand-edit it

### Risk: Install filtering becomes confusing

Mitigation:

- keep the component set small: `base`, `documents`, `skills`
- document exactly what each component includes per harness

### Risk: Doctor grows into a mini-framework

Mitigation:

- keep checks small, composable, and read-only
- avoid adding repair logic in the first version

## Acceptance Checklist

- [ ] harness compatibility rules are richer and centralized
- [ ] build emits a stable manifest
- [ ] install supports `--dry-run`
- [ ] install supports `--component`
- [ ] doctor validates source and build state
- [ ] doctor optionally validates installed state
- [ ] tests cover new contracts without brittle output counts
- [ ] docs explain the new verification and install workflows

## Final Recommendation

Implement this work in the following order:

1. compatibility contract
2. build manifest
3. install plan and dry-run
4. selective install
5. doctor
6. tests and docs cleanup

That order keeps the system small and coherent.

The important idea is not to copy bigger projects feature-for-feature. It is to preserve this repo's strongest property - one canonical source tree - while adding the operational maturity that makes multi-harness output easier to trust.
