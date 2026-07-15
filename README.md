# AI harness configs

Personal prompt and skill configuration for OpenCode, Claude Code, and Codex.

The repository deliberately uses provider-native templates instead of a framework.
Templates mirror the files each harness consumes, prompt bodies are shared, and a
small script expands two token types:

- `{{prompt:name}}` inserts `source/prompts/name.md`
- `{{model:profile}}` selects a model from `source/models.toml`

## Requirements

- Python 3.11 or newer
- Bash for the optional installer

There are no third-party Python dependencies.

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

Generated files are written to `build/`. Every build starts from a clean output
directory and fails if a prompt, include, model, or TOML template is invalid.

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

## Edit prompts

Reusable prompt bodies live in `source/prompts/`. They are ordinary Markdown
without configuration frontmatter. Shared fragments use:

```text
{{include:_report-only-intro.md}}
```

Provider-specific frontmatter and file formats live under `templates/` in their
final output layout. Editing a template is intentionally direct: what you see is
what the harness receives.

## Change models

`source/models.toml` contains the small set of model profiles referenced by the
templates. Each profile can provide `opencode`, `claude`, and `codex` values,
plus optional `*_work` overrides. Work values fall back to the normal harness
value when omitted.

## Add a prompt

1. Add the shared body as `source/prompts/<name>.md`.
2. Add explicit templates only for the harnesses that should receive it.
3. Reference the body with `{{prompt:<name>}}`.
4. Run `./build.py`.

There is no harness registry, schema version, manifest, plugin API, or generated
domain model. The checked-in templates are the configuration contract.
