# AI-Agents

Multi-harness prompt generation for **OpenCode**, **Claude Code**, and **Codex**.

This repository keeps prompts, subagents, commands, modes, and skills in one source tree and renders them into harness-specific output.

## Current Direction

- OpenCode is the default harness
- Claude and Codex are first-class targets
- `--work` switches model resolution to work profiles from `source/model-profiles.toml`
- the primary interface is the Python CLI in `ai_agents/`
- `opencode-init.sh` remains the OpenCode config initialization path

## Requirements

- Python 3.11+
- no third-party Python dependencies

## Commands

Run through the module:

```bash
python3 -m ai_agents <command>
```

Or use the compatibility entrypoint:

```bash
python3 build.py <command>
```

### Build

Build OpenCode only:

```bash
python3 -m ai_agents build
```

Build all harnesses:

```bash
python3 -m ai_agents build --all
```

Build a specific harness set:

```bash
python3 -m ai_agents build --harness claude --harness codex
```

Build with work model profiles:

```bash
python3 -m ai_agents build --all --work
```

### Install

Install OpenCode only:

```bash
python3 -m ai_agents install
```

Install all harnesses:

```bash
python3 -m ai_agents install --all
```

Install using existing build output:

```bash
python3 -m ai_agents install --all --skip-build
```

Preview install actions without writing files:

```bash
python3 -m ai_agents install --all --dry-run
```

Install only selected components:

```bash
python3 -m ai_agents install --all --component base --component skills
```

Force overwrite during install:

```bash
python3 -m ai_agents install --all --force
```

### Lint

Validate prompt metadata and check for harness-coupled content patterns:

```bash
python3 -m ai_agents lint
```

### Doctor

Verify source, build, and optional installed state:

```bash
python3 -m ai_agents doctor
python3 -m ai_agents doctor --installed
python3 -m ai_agents doctor --json
```

### List Harnesses

```bash
python3 -m ai_agents list harnesses
```

### OpenCode Config

Use the existing helper script:

```bash
./opencode-init.sh
```

The helper refuses to overwrite symlink targets and installs `opencode.json` with mode `600`.

## Output Layout

Build output is written to `build/` by default.

Custom build output paths may point elsewhere when creating a fresh directory, but existing output directories must stay inside `build/`.

Each successful build also writes `build/manifest.json`, which records generated artifacts, source-to-output mappings, harnesses, and logical components.

### OpenCode

```text
build/opencode/
  AGENTS.md
  agent/*.md
  command/*.md
  skill/*
```

### Claude

```text
build/claude/
  CLAUDE.md
  agents/*.md
  commands/*.md
  skills/*
```

### Codex

```text
build/codex/
  AGENTS.md
  .codex/agents/*.toml
  .agents/skills/*
```

## Source Layout

- `source/prompts/` contains prompt documents and base instructions
- `source/skills/` contains reusable skill directories
- `source/model-profiles.toml` contains logical model profiles for default and work environments

Prompt sources use a minimal harness-neutral schema: `description`, `kind`, `model_profile`, and `targets.<harness>`.

Unsupported compatibility-only fields such as top-level `[shared]` blocks or target `partials` are rejected until there is a real consumer for them.

Harness-specific compatibility rules live in `ai_agents/domain/harnesses.py`. The harness registry is also the source of truth for logical output/install components such as `base`, `documents`, and `skills`.

## Model Profiles

Model selection and reusable harness tuning are driven by logical profiles instead of prompt-local provider rewrites.

Profiles can define shared defaults in `profiles.<name>.shared` for cross-platform tuning like `reasoning_effort`, `temperature`, and related sampling settings. Harness-specific tables keep only the settings that truly differ by target, such as model names or sandbox controls.

For OpenCode profiles, provider selection is split from the model name:

```toml
[profiles.default.default.opencode]
provider = "openai"
model = "gpt-5.4"
```

The resolver composes that into the final OpenCode model string. Claude and Codex continue to use literal `model` values and do not support `provider`.

Examples:

- `default`
- `deep_review`
- `creative`
- `planner`

Each profile resolves per harness and per environment.

`--work` switches from `default` environment values to `work` environment values.

## Installed Locations

### OpenCode

- `~/.config/opencode/`

### Claude

- `~/.claude/`

### Codex

- `~/.codex/AGENTS.md`
- `~/.codex/agents/`
- `~/.agents/skills/`

## Development

Run tests:

```bash
python3 -m unittest discover -s tests
```

Run a full build verification:

```bash
python3 -m ai_agents lint
python3 -m ai_agents build --all --work
python3 -m ai_agents doctor
```
