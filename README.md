# AI-Agents

Multi-harness prompt generation for **OpenCode**, **Claude Code**, and **Codex**.

This repository keeps prompts, subagents, commands, modes, and skills in one source tree and renders them into harness-specific output.

## Current Direction

- OpenCode is the default harness
- Claude and Codex are first-class targets
- `--work` switches model resolution to work profiles from `source/model-profiles.toml`
- the primary interface is the Python CLI in `ai_agents/`
- `opencode-init.sh` remains available for OpenCode config initialization

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

Force overwrite during install:

```bash
python3 -m ai_agents install --all --force
```

### Lint

Validate prompt metadata and check for harness-coupled content patterns:

```bash
python3 -m ai_agents lint
```

### List Harnesses

```bash
python3 -m ai_agents list harnesses
```

### OpenCode Config

The existing helper script still works:

```bash
./opencode-init.sh
```

The new CLI also supports initialization:

```bash
python3 -m ai_agents init opencode
```

## Output Layout

Build output is written to `build/` by default.

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

The build system supports:

- the new harness-neutral schema with `kind`, `model_profile`, and `targets.<harness>`
- the legacy prompt schema already present in `source/prompts/`, which is normalized during build

## Model Profiles

Model selection is driven by logical profiles instead of prompt-local provider rewrites.

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
```
