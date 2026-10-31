# AI harness configs

Personal prompt and skill configuration for OpenCode, Claude Code, and Codex.

Create each subagent or skill once. Subagents use a shared definition and one
default native template per harness, with optional overrides. Skills are shared
folders copied to each harness. Commands and modes keep explicit native templates.

## Requirements

- Python 3.11 or newer
- OpenCode V2 for the OpenCode configuration
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
duplicate output paths or file/directory collisions fail before the previous build
is replaced. Finder's `.DS_Store` files are ignored when scanning templates and
overrides. YAML templates remain directly editable; the build does not validate
their harness-specific fields.

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

`source/prompts/AGENTS.md` is the shared base for all three harnesses: the build
copies it to OpenCode/Codex `AGENTS.md` and Claude `CLAUDE.md`. Edit the source
and rebuild/reinstall rather than editing generated copies. OpenCode V2
recognizes the exact name `AGENTS.md`, not `Agent.md` or a `CLAUDE.md` fallback.

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

## Add a command or mode

1. Add the shared body as `source/prompts/<name>.md`.
2. Add explicit templates under `templates/<harness>/` in the desired output layout.
3. Reference the body with `{{prompt:<name>}}`.
4. Run `./build.py`.

These templates can use `{{prompt:name}}` for a shared prompt body and
`{{model:profile}}` for a model. Command/skill and mode mappings differ by harness,
so these remain explicit. `new.py agent` creates subagents only.

## Add a shared skill

Create `source/skills/<name>/SKILL.md`, using a lowercase, hyphen-separated name
such as `review-migrations`. Start with YAML frontmatter describing the skill's
name and when to use it, followed by the instructions:

```markdown
---
name: review-migrations
description: Use when reviewing database migrations for correctness and deployment risks.
---

# Review database migrations

1. Read the migration and related schema.
2. Check for data loss, locking, and compatibility issues.
3. Check the rollback approach.
4. Report concrete findings with file references and suggested fixes.
```

The build copies the entire skill folder into all three harnesses; no separate
template is needed. Keep instructions portable: describe actions such as
"search the repository" instead of naming a harness-specific tool. Keep model
selection and agent configuration in the harness-specific templates. Supporting
scripts, references, and assets can live inside the skill folder; reference them
from `SKILL.md` using relative paths.

Shared skills are copied verbatim. Tokens such as `{{prompt:...}}`,
`{{model:...}}`, and `{{include:...}}` are not expanded there. Choose a skill name
that does not overlap a skill under `templates/`; duplicate output file paths
fail the build rather than overwriting shared files.

Run `./build.py` to generate all three configurations, or `./install.sh` to build
and install them. Then try a representative request in each harness to confirm
that it discovers the skill and follows the intended steps. The build does not
validate skill metadata or behavior.

## Agent definition layout

The nine shared subagent definitions live in `source/agents/`, with common metadata
in TOML frontmatter and instructions below it. Three native defaults and five
overrides provide their harness-specific settings. Edit an agent's source file for
shared changes and its relevant override for exceptions. Commands and modes keep
explicit templates under `templates/<harness>/`.

## Checks

```bash
python3 -m unittest discover -s tests
```

The test suite creates temporary copies to check agent creation, Unicode and native
escaping, target selection, override isolation, skill copying, overwrite refusal,
Finder metadata handling, and preservation of the previous build after rendering
or collision errors. Installer checks use isolated home directories, leaving real
harness configs untouched.

Before the shared-agent authoring change was merged, generated configs were also
compared byte-for-byte against the previous main (`50b8e9d`) across all 56
combinations of harness subsets, work mode, and provider options. This was a
migration check; the test suite does not automatically compare against Git history.

## Adoption checklist

See [TODO.md](TODO.md) for the remaining rollout checks. Before adopting these
configs, install each harness independently and confirm that it discovers the
rendered agents, commands, and skills. Also verify the work profile and the
OpenCode provider override against the providers used in the real environment.

Keep future changes focused on concrete authoring or harness compatibility needs.
