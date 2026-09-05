# AI harness configs

Personal prompt and skill configuration for OpenCode, Claude Code, and Codex.

Create each subagent or skill once. Subagents use a shared definition and one
default native template per harness, with optional overrides. Skills are shared
folders copied to each harness. Commands and modes keep explicit native templates.

## Requirements

- Python 3.11 or newer
- Bash for the optional installer

There are no third-party Python dependencies.

The executable scripts use `python3`. If yours is older than 3.11, invoke them
with a newer interpreter, for example `python3.11 new.py agent database-review`
and `python3.11 build.py`.

## Create a subagent

```bash
./new.py agent database-review --profile deep_review
```

Edit the generated `source/agents/database-review.md`, then run `./build.py`.
No per-harness files are needed. The filename is the agent name; its frontmatter
contains a description, a model profile from `source/models.toml`, and targets:

```markdown
+++
description = "Review database queries and identify performance problems."
model_profile = "deep_review"
harnesses = ["claude", "opencode", "codex"]
+++

Review query plans, indexes, and transaction boundaries.
Explain each finding and suggest a concrete improvement.
```

`description` and `model_profile` are required. Omitting `harnesses` selects all
three. To create an agent for selected harnesses, repeat `--harness`:

```bash
./new.py agent database-review --harness claude --harness codex \
  --description "Review database queries and identify performance problems."
```

These are alternative creation examples; rerunning either for the same name
will refuse to overwrite the file. `--profile` defaults to `deep_review`.

## Create a skill

```bash
./new.py skill database-debugging \
  --description "Investigate slow database queries and explain their causes."
```

Edit `source/skills/database-debugging/SKILL.md`, then run `./build.py`.
The whole folder is copied to each selected harness, so supporting scripts,
examples, and reference files can live beside `SKILL.md`. Skills do not need
per-harness templates.

Both creation commands use lowercase names with hyphens and refuse to overwrite
existing content. They create editable starting files with TODO instructions;
finish those before installing. `--description` is optional for either command.

## Build

Build all harnesses:

```bash
./build.py
```

Build selected harnesses:

```bash
./build.py opencode
./build.py claude codex
```

Use work model mappings:

```bash
./build.py --work
```

Override OpenCode's provider prefix:

```bash
./build.py opencode --opencode-provider github-copilot
```

Generated files are written to a fresh `build/` directory after rendering succeeds.
Invalid agent metadata, missing references, recursive includes, invalid TOML, and
duplicate output paths fail the build. YAML templates remain directly editable;
the build does not validate their harness-specific fields.

## Install

Build and install all configs:

```bash
./install.sh
```

Install selected harnesses:

```bash
./install.sh opencode
./install.sh claude codex
```

Existing managed paths require confirmation. Use `--force` to replace them
without prompting:

```bash
./install.sh opencode --work --force
```

Set `PYTHON` if `python3` is not Python 3.11 or newer:

```bash
PYTHON=/path/to/python3.11 ./install.sh
```

`opencode.json` remains an explicit, one-time setup:

```bash
./opencode-init.sh
```

## Customize an agent for one harness

Default templates live in:

```text
templates/defaults/claude/agent.md
templates/defaults/opencode/agent.md
templates/defaults/codex/agent.toml
```

Changing a default affects every agent using it for that harness. For an exception,
copy the default to `templates/overrides/<harness>/<agent-name>.<md-or-toml>` and
edit its native settings. For example, `templates/overrides/claude/database-review.md`
could specify a different `tools` list. It replaces the entire Claude template
for that agent; the other harnesses still use their defaults. Keep the placeholder
tokens when copying so the name, description, model, and instructions stay shared.

| Token | Value |
|---|---|
| `{{agent:name}}` | Source filename without `.md` |
| `{{agent:description}}` | Shared description |
| `{{agent:model}}` | Profile resolved for this harness and build options |
| `{{agent:body}}` | Shared instructions, with includes expanded |

Use metadata tokens as whole unquoted YAML values. In TOML, keep them inside
double-quoted strings and keep the body token inside a multiline double-quoted
string, as shown in the default template. The renderer escapes inserted values
for those positions.

Permissions, tool lists, and reasoning settings stay in native templates. The
defaults preserve the existing settings; they do not promise equivalent permission
behavior across harnesses. An override for a missing agent or a disabled target
is an error: remove or rename it when changing the agent's name or targets.

## Edit shared instructions

Subagent instructions live below the frontmatter in `source/agents/`. Command
and mode bodies, base instructions, and shared fragments live in `source/prompts/`.
Agent bodies and explicit prompt bodies can include a fragment from `source/prompts/`:

```text
{{include:_report-only-intro.md}}
```

For example, the referenced `_report-only-intro.md` is shared across review agents.

## Change models

`source/models.toml` contains the small set of model profiles referenced by the
templates. Each profile can provide `opencode`, `claude`, and `codex` values,
plus optional `*_work` overrides. Work values fall back to the normal harness
value when omitted.

## Add a command or mode

1. Add the shared body as `source/prompts/<name>.md`.
2. Add explicit templates under `templates/<harness>/` in the desired output layout.
3. Reference the body with `{{prompt:<name>}}`.
4. Run `./build.py`.

These templates can use `{{prompt:name}}` for a shared prompt body and
`{{model:profile}}` for a model. Command/skill and mode mappings differ by harness,
so these remain explicit. `new.py agent` creates subagents only.

## Migration from the template branch

The nine subagent bodies moved from `source/prompts/` to `source/agents/`, with
their common metadata added as TOML frontmatter. Their 27 individual templates
became three defaults and ten overrides for existing tool/reasoning differences.
Edit the new source file for shared changes and the relevant override for exceptions.
Commands, modes, shared skills, model profiles, output paths, and installation
commands retain their existing layout and behavior.

## Checks

```bash
python3 -m unittest discover -s tests
```

The small test suite creates temporary copies to check agent creation, native
escaping, target selection, override isolation, skill copying, and overwrite
refusal. It does not install anything. During this migration, generated configs
were also compared byte-for-byte against the template branch for default, work,
provider override, and combined work/provider builds.

## Adoption checklist

See [TODO.md](TODO.md) for the remaining rollout checks. Before merging this
branch, install each harness independently and confirm that it discovers the
rendered agents, commands, and skills. Also verify the work profile and the
OpenCode provider override against the providers used in the real environment.

Keep future changes focused on concrete authoring or harness compatibility needs.
