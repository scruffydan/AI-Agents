# AI harness configs

Personal prompt and skill configuration for OpenCode, Claude Code, and Codex.

The repository deliberately uses provider-native templates instead of a framework.
Templates mirror the files each harness consumes, prompt bodies are shared, and a
small script expands two token types:

- `{{prompt:name}}` inserts `source/prompts/name.md`
- `{{model:profile}}` selects a model from `source/models.toml`

## Requirements

- Python 3.11 or newer
- OpenCode V2 for the OpenCode configuration
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

OpenCode output uses V2's `agents/`, `commands/`, and `skills/` directories.
Agent permissions use ordered `permissions` rules, and reasoning effort is
selected with a model variant such as `openai/gpt-6.1-sol#high`.

## Skills and modes

All three harnesses receive every shared skill under `source/skills/`, plus
brainstorming, thorough planning, and full code review skills. The shared skills
are copied without changing their instructions.

- OpenCode: load `@mode-brainstorm`, `@mode-thorough-plan`, or
  `@command-code-full-review`. The `brainstorm` and `thorough-plan` primary agents
  and `/code-full-review` command remain available.
- Claude Code: use `/mode-brainstorm`, `/mode-thorough-plan`, or `/code-full-review`.
- Codex: use `$mode-brainstorm`, `$mode-thorough-plan`, or
  `$command-code-full-review`.

Claude's brainstorming skill selects its configured model for the current turn.
Codex's brainstorming skill uses the `brainstorm` custom agent to select its
configured model. OpenCode retains an existing session's selected model when
changing agents, so select the brainstorm model in `/models` as well as the
`brainstorm` agent.

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

Agents, commands, and skills are installed one entry at a time, so anything
else in those directories is left alone. Unchanged files are skipped. Changed
files require confirmation, and the replaced version is moved to
`~/.ai-agents-backups/<timestamp>/` instead of being deleted. Removing a prompt
from this repository does not remove its installed copy; delete that by hand.

OpenCode entries install into `~/.config/opencode/agents`, `commands`, and
`skills`. Existing V1 `agent`, `command`, and `skill` directories are left in
place; review and remove obsolete entries after verifying V2 discovery to avoid
loading stale definitions alongside the new files.

Use `--force` to replace changed files without prompting:

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

This replaces the entire OpenCode config, including local provider settings.
For an existing setup, merge the rules from `source/opencode.json` manually or
review the replacement first. The initializer confirms replacements, backs up
the old file under `~/.ai-agents-backups/` with private permissions, and installs
the new file with mode `600`. `--yes` skips confirmation but still backs up;
unchanged files are skipped. It refuses a symlink at the destination file.
`install.sh` does not install or update `opencode.json`.

## Edit prompts

Reusable prompt bodies live in `source/prompts/`. They are ordinary Markdown
without configuration frontmatter. Shared fragments use:

```text
{{include:_report-only-intro.md}}
```

`source/prompts/AGENTS.md` is the shared base for all three harnesses: the build
copies it to OpenCode/Codex `AGENTS.md` and Claude `CLAUDE.md`. Edit the source
and rebuild/reinstall rather than editing generated copies. OpenCode V2
recognizes the exact name `AGENTS.md`, not `Agent.md` or a `CLAUDE.md` fallback.

Provider-specific frontmatter and file formats live under `templates/` in their
final output layout. Editing a template is intentionally direct: what you see is
what the harness receives.

## Change models

`source/models.toml` contains the small set of model profiles referenced by the
templates. Each profile can provide `opencode`, `claude`, and `codex` values,
plus optional `*_work` overrides. Work values fall back to the normal harness
value when omitted.

OpenCode profile values include the reasoning variant, so work mappings can use
a different effort from normal mappings. Sol and Opus roles use high effort;
Astra brainstorming stays at medium. The OpenCode work docs-fetcher and git-commit
agents use Claude Sonnet 5.5 at high effort; explore uses Gemini 4 Argon at high
effort. Claude templates set `effort: high` for Opus
roles, and Codex templates set high reasoning effort for Sol roles.

OpenCode V2 uses the `google-vertex` provider for both Gemini and Claude work
models. Configure Google Cloud project, location, credentials, and model access
on the work machine; the repository's build does not verify live provider access.

## Add a prompt

1. Add the shared body as `source/prompts/<name>.md`.
2. Add explicit templates only for the harnesses that should receive it.
3. Reference the body with `{{prompt:<name>}}`.
4. Run `./build.py`.

There is no harness registry, schema version, manifest, plugin API, or generated
domain model. The checked-in templates are the configuration contract.

## Adoption checklist

See [TODO.md](TODO.md) for the remaining rollout checks. Before merging this
branch, install each harness independently and confirm that it discovers the
rendered agents, commands, and skills. Also verify the work profile and the
OpenCode provider override against the providers used in the real environment.

These are manual compatibility checks, not a plan to rebuild the removed
framework. Future code should be added only when a concrete harness-format change
cannot be represented directly in a provider-native template.
