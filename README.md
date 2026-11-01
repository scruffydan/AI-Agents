# AI harness configs

Personal prompt and skill configuration for Codex, Claude Code, and OpenCode.

Define subagents and skills once, then build and install them for each harness.
Subagents combine shared instructions with native templates and optional overrides.
Skills are copied as complete folders. Commands and modes use explicit native
templates.

## Requirements

- Python 3.11 or newer
- OpenCode V2 for the OpenCode configuration
- Bash for the optional installer

There are no third-party Python dependencies.

The executable scripts use `python3`. If yours is older than 3.11, invoke them
with a newer interpreter, for example `python3.11 new.py agent database-review`
and `python3.11 build.py`.

## Build

Build all harnesses:

```bash
./build.py
```

Build selected harnesses:

```bash
./build.py codex
./build.py codex claude
./build.py opencode
```

Use work model mappings:

```bash
./build.py --work
```

Override OpenCode's provider prefix with `openai` or `opencode`:

```bash
./build.py opencode --opencode-provider opencode
```

Each build replaces `build/` with output for the selected harnesses. Agent
metadata, references, includes, TOML, and output paths are checked before the
previous build is replaced. YAML templates and shared skill metadata are not
validated for harness-specific requirements.

OpenCode output uses V2's `agents/` and `skills/` directories, plus `commands/`
when command templates are present.
Agent permissions use ordered `permissions` rules, and reasoning effort is
selected with a model variant such as `openai/gpt-6.1-sol#high`.

## Install

Choose which harnesses to build and install interactively:

```bash
./install.sh
```

The picker lists Codex first (the default), Claude Code second, and OpenCode last.
Enter one or more numbers or names separated by spaces, or press Enter for Codex.

Skip the picker by naming harnesses, or use `--all` to install all three:

```bash
./install.sh codex
./install.sh codex claude
./install.sh --all
```

`--all` cannot be combined with explicit harness names. For unattended use, pass
harness names or `--all`.

Agents, commands, and skills are installed one entry at a time, so anything
else in those directories is left alone. Unchanged files are skipped. Changed
files require confirmation, and the replaced version is moved to
`~/.ai-agents-backups/<timestamp>/` instead of being deleted. Removing a prompt
from this repository does not remove its installed copy; clean up obsolete
entries explicitly.

Installation destinations:

| Harness | Base instructions | Agents and commands | Skills |
|---|---|---|---|
| Codex | `~/.codex/AGENTS.md` | `~/.codex/agents/` | `~/.agents/skills/` |
| Claude Code | `~/.claude/CLAUDE.md` | `~/.claude/agents/` | `~/.claude/skills/` |
| OpenCode | `~/.config/opencode/AGENTS.md` | `~/.config/opencode/agents/`, `commands/` | `~/.config/opencode/skills/` |

Use `--force` to replace changed files without prompting:

```bash
./install.sh codex --work --force
```

Set `PYTHON` if `python3` is not Python 3.11 or newer:

```bash
PYTHON=/path/to/python3.11 ./install.sh
```

Set up `opencode.json` separately:

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

## T3 Code remote host setup

The separate [T3 background-service guide](docs/t3-background-service.md) covers
the official app on Dan's Mac, with a service-owned backend and the Dock app as
a client. `node t3-service-env.mjs --help` describes the standalone candidate
generator (Node 22.16+, no packages). It prepares service-scoped GitHub HTTPS/`gh`
authentication while preserving SSH remotes and ordinary terminal behavior.
Activation and rollback are manual; `install.sh` does not configure T3.

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
harnesses = ["codex", "claude", "opencode"]
+++

Review query plans, indexes, and transaction boundaries.
Explain each finding and suggest a concrete improvement.
```

`description` and `model_profile` are required. Omitting `harnesses` selects all
three. To create an agent for selected harnesses, repeat `--harness`:

```bash
./new.py agent database-review --harness codex --harness claude \
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
You can also create `source/skills/<name>/SKILL.md` by hand, with YAML frontmatter
containing `name` and `description`, followed by the instructions.

The whole folder is copied to each selected harness without changing its contents.
Supporting scripts, examples, and reference files can live beside `SKILL.md`; use
relative paths to reference them. Keep instructions portable and put model
selection and agent settings in the native templates.

Shared skills do not need per-harness templates. Tokens such as `{{prompt:...}}`,
`{{model:...}}`, and `{{include:...}}` are not expanded in shared skills. Avoid names
that overlap skills under `templates/`; duplicate output paths fail the build.
The build does not validate skill metadata or behavior.

Both creation commands use lowercase names with hyphens and refuse to overwrite
existing content. They create editable starting files with TODO instructions;
finish those before installing. `--description` is optional for either command.

## Skills and modes

All three harnesses receive the shared skills under `source/skills/`.

- Codex: use `$brainstorming`, `$mode-thorough-plan`, or `$code-review`.
- Claude Code: use `/brainstorming`, `/mode-thorough-plan`, or `/code-review`.
- OpenCode: load `@brainstorming`, `@mode-thorough-plan`, or `@code-review`.
  The `brainstorm` and `thorough-plan` primary agents are also available.

Choose a workflow for the task:

- `brainstorming` explores requirements and design alternatives in the current
  conversation. Explicit requests for the configured brainstorming agent use
  read-only creative exploration.
- `mode-thorough-plan` produces an implementation plan without editing files.
  OpenCode's `thorough-plan` agent loads this skill with edit and shell access
  denied.
- `code-review` reviews code or evaluates supplied feedback. Targeted reviews use
  relevant perspectives; explicit full reviews cover all five specialists.
  Feedback evaluation checks the supplied claims and proposed fixes. Both routes
  are report-only unless fixes are authorized.
- `systematic-debugging` guides bug investigation. `five-whys` supports explicit
  causal analysis for coding and noncoding problems. Its shared technique lives
  in `systematic-debugging/five-whys.md`, so keep both skill folders installed.
- `git-commit` handles verification, staging, and committing in the current
  conversation, using the configured drafting agent when available. `git-push`
  checks readiness for a separately authorized push.
- `update-readme` checks README and existing AGENTS.md accuracy;
  `verification-before-completion` checks the evidence behind completion claims.

External documentation research uses the `docs-fetcher` subagent under the shared
AGENTS.md instructions. The child receives the question, target version, official
URLs, and constraints, then returns focused findings and primary-source links.
If delegation or web access is unavailable, report the limitation and continue
independent work.

For configured brainstorming in Codex and Claude Code, the `brainstorm` agent
selects its model through native templates. OpenCode retains an existing session's
model when changing agents; select the configured model in `/models` as well as
the `brainstorm` primary agent.

## Customize an agent for one harness

Default templates live in:

```text
templates/defaults/codex/agent.toml
templates/defaults/claude/agent.md
templates/defaults/opencode/agent.md
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

Tool lists and reasoning settings stay in native templates. Claude's review
agents use file reading and search tools; its documentation and sidebar agents
can search the web and fetch pages. OpenCode permissions also live in templates.
Codex custom agents inherit the parent session's sandbox and approval policy;
their agent files do not establish a separate permission boundary. Report-only
instructions still apply. An override for a missing agent or a disabled target
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
and rebuild and reinstall to update the harnesses.

## Change models

Edit `source/models.toml` to change the models behind each profile. An agent selects
its profile with `model_profile` in `source/agents/<name>.md`; explicit templates
use `{{model:profile}}`.

Each profile provides model IDs for its target harnesses using `codex`, `claude`,
and `opencode` keys. Optional `codex_work`, `claude_work`, and `opencode_work` values
apply with `--work`, falling back to the normal value when omitted.

OpenCode model IDs include their reasoning variant. Claude and Codex reasoning
settings live in native defaults, overrides, or explicit templates.

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

## Checks

```bash
python3 -m unittest discover -s tests
```

Tests use temporary repositories and isolated home directories, leaving real
harness configs untouched. The T3 setup tests additionally require Node 22.16+
and Git and use a fake `gh` without network access; they skip if Node or Git is
absent. No live T3 service or host authentication is exercised by the suite.
