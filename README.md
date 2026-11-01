# AI harness configs

Personal prompt and skill configuration for Codex, Claude Code, and OpenCode.

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

Generated files are written to a fresh `build/` directory after rendering succeeds.
Invalid agent metadata, missing references, recursive includes, invalid TOML, and
duplicate output paths or file/directory collisions fail before the previous build
is replaced. Finder's `.DS_Store` files are ignored when scanning templates and
overrides. YAML templates remain directly editable; the build does not validate
their harness-specific fields.

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

`--all` installs in Codex, Claude Code, OpenCode order and cannot be combined with
explicit harness names. For unattended use, pass harness names or `--all`; the
picker exits without installing if input ends before a selection is received.

Agents, commands, and skills are installed one entry at a time, so anything
else in those directories is left alone. Unchanged files are skipped. Changed
files require confirmation, and the replaced version is moved to
`~/.ai-agents-backups/<timestamp>/` instead of being deleted. Removing a prompt
from this repository does not remove its installed copy; clean up obsolete
entries explicitly. The installer has no special cases for retired prompts.

OpenCode entries install into `~/.config/opencode/agents`, `commands`, and
`skills`. Existing V1 `agent`, `command`, and `skill` directories are left in
place; review and remove obsolete entries after verifying V2 discovery to avoid
loading stale definitions alongside the new files.

Use `--force` to replace changed files without prompting:

```bash
./install.sh codex --work --force
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

All three harnesses receive every shared skill under `source/skills/`, including
`mode-thorough-plan`, plus native templates for `brainstorm-with-agent`. The
shared skills are copied without changing their instructions. OpenCode's
`thorough-plan` primary agent loads the shared planning skill while retaining
its edit and shell restrictions.

- Codex: use `$brainstorm-with-agent`, `$mode-thorough-plan`, or `$code-review`.
- Claude Code: use `/brainstorm-with-agent`, `/mode-thorough-plan`, or `/code-review`.
- OpenCode: load `@brainstorm-with-agent`, `@mode-thorough-plan`, or `@code-review`.
  The `brainstorm` and `thorough-plan` primary agents remain available. Request a
  full review through `code-review`; the `/code-full-review` shortcut is retired.

`code-review` handles targeted reviews and explicit full reviews. Ordinary reviews
use relevant perspectives; full reviews cover all five specialists. Findings are
report-only unless fixes are also requested. Agent tools and permissions come
from the current harness rather than assumptions in a shared skill.

`brainstorming` supports design decisions in the current conversation when
requirements or approaches need exploration. Routine edits and fully specified
small changes do not need that workflow. `brainstorm-with-agent` uses the
configured brainstorming model; `mode-thorough-plan` produces a plan without
editing files and asks only questions that materially affect the outcome.

`update-readme` owns README and existing AGENTS.md checks, while
`verification-before-completion` owns verification evidence. Git skills reference
these checks and reuse valid results when relevant inputs are unchanged. Commit
messages follow the repository's conventions, including free-form subjects.

Shared workflows scale planning, testing, and review to the task's stakes. They
reuse established decisions and authorization rather than adding fixed approval
or review loops. Specialist reviewers share one report format while retaining
their domain checklists, language-specific guidance, and examples. Skill authoring
and debugging retain their detailed testing and investigation techniques. The
commit helper returns its proposal to the main agent, which handles user
interaction and the actual commit.

Claude's brainstorming skill selects its configured model for the current turn.
Codex's brainstorming skill uses the `brainstorm` custom agent to select its
configured model. OpenCode retains an existing session's selected model when
changing agents, so select the brainstorm model in `/models` as well as the
`brainstorm` agent.

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
harness configs untouched.
