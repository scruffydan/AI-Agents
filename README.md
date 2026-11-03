# AI harness configs

Personal agents, skills, and instructions for Codex, Claude Code, and OpenCode.
Edit shared source files, then build and install them for the harnesses you use.

Requires Python 3.11+ and OpenCode V2 for OpenCode output.
There are no third-party Python dependencies.

## Install

Run the picker, or name the harnesses to install:

```bash
./install.py                 # Interactive; Enter selects Codex
./install.py codex claude    # Install selected harnesses
./install.py --all           # Install all three
```

Choose one form; `--all` cannot be combined with harness names. Explicit names
or `--all` also work unattended. Add `--work` for work models or `--force` to
replace changed files without confirmation. To use a specific Python interpreter,
run `/path/to/python3.11 install.py` with the same arguments.

The installer skips unchanged entries, asks before replacing changed entries,
and saves replacements under `~/.ai-agents-backups/<timestamp>-<suffix>/`. Unrelated
entries are left alone. Removing an entry from this repository does not remove
its installed copy.

| Harness | Base instructions | Agents | Skills |
|---|---|---|---|
| Codex | `~/.codex/AGENTS.md` | `~/.codex/agents/` | `~/.agents/skills/` |
| Claude Code | `~/.claude/CLAUDE.md` | `~/.claude/agents/` | `~/.claude/skills/` |
| OpenCode | `~/.config/opencode/AGENTS.md` | `~/.config/opencode/agents/` | `~/.config/opencode/skills/` |

If previously installed, move retired `explore` and `sidebar` agents and the
`implementation-workflow` skill out of these directories. Preserve any local
changes you want to keep. The repository no longer generates custom commands;
older installed commands are also left alone.

### OpenCode settings

`install.py` leaves `opencode.json` alone. To install the repository's settings
(requires Bash):

```bash
./opencode-init.sh
```

This replaces the entire config, including provider settings. For an existing
setup, review the replacement or merge [source/opencode.json](source/opencode.json)
manually. The initializer asks before replacing a changed file, backs it up with
private permissions, and installs the config with mode `600`. `--yes` skips
confirmation and still backs up; unchanged files are skipped, and destination
symlinks are refused.

Older configs must remove any global `read "*"` allowance to restore native
`.env` prompts. Later agent-specific rules can still override those prompts.

## Build without installing

```bash
./build.py                              # All harnesses
./build.py codex claude                  # Selected harnesses
./build.py --work                        # Work model mappings
./build.py opencode --opencode-provider opencode
```

Each build replaces `build/` with output for the selected harnesses.
`--opencode-provider` accepts `openai` or `opencode` and cannot be combined with
`--work`, whose OpenCode models use Google Vertex. Configure Vertex credentials,
project, location, and model access separately on the work machine.

## Customize

| What to change | Where to edit |
|---|---|
| Agent instructions and model profile | `source/agents/<name>.md` |
| Shared skills and supporting files | `source/skills/<name>/` |
| Base instructions for all harnesses | [source/prompts/AGENTS.md](source/prompts/AGENTS.md) |
| Shared instruction fragments | `source/prompts/` |
| Models, including work mappings | [source/models.toml](source/models.toml) |
| Harness formats, tools, effort, and permissions | [renderers.py](renderers.py) |

Rebuild and reinstall after editing. `build/` is generated.

### Add an agent

```bash
./new.py agent database-review \
  --description "Review database queries and identify performance problems."
```

Edit `source/agents/database-review.md`. Its TOML frontmatter selects the
`description`, `model_profile`, and `harnesses`; instructions go below it.
The default profile is `deep_review`. Use `--profile` to choose another, and
repeat `--harness` to select targets. Omitting targets selects all three.
New shared agents use each renderer's defaults without Python changes.

### Add a skill

```bash
./new.py skill database-debugging \
  --description "Investigate slow database queries and explain their causes."
```

Edit `source/skills/database-debugging/SKILL.md`. Keep YAML frontmatter to `name`
and `description`, and keep instructions portable across harnesses. Supporting
files can sit beside `SKILL.md` and use relative links. The whole folder is
copied unchanged, without token expansion, except for macOS `.DS_Store` and Windows
`Thumbs.db`, `ehthumbs.db`, and `Desktop.ini` metadata (Windows names match regardless
of capitalization). Builds and installs exclude these files; content comparisons
ignore them so OS metadata does not trigger unnecessary reinstalls.

Both creation commands require lowercase names with single hyphens, refuse to
overwrite existing content, and create TODO instructions to finish before
installing. `--description` is optional.

### Models and harness settings

Agent model profiles refer to entries in `source/models.toml`. Each profile has
`codex`, `claude`, and `opencode` model IDs for its targets. Optional `*_work`
values apply with `--work`, falling back to the normal value when omitted.
OpenCode model IDs include their reasoning variant, such as `#high`.

For native settings, edit `render_codex`, `render_claude`, or `render_opencode`
in `renderers.py`. Each function keeps its defaults and named exceptions together.
A new primary mode needs a renderer case and, if it has no shared agent definition,
an output entry in `build.py`. OpenCode reserves `thorough-plan` for its planning
agent.

Agent instructions can include shared fragments from `source/prompts/`:

```text
{{include:_report-only-intro.md}}
```

## Use skills and modes

Browse [source/skills](source/skills) for the available workflows, including
brainstorming, planning, code review, debugging, and Git tasks.

| Harness | Example |
|---|---|
| Codex | `$code-review` |
| Claude Code | `/code-review` |
| OpenCode | Load `@code-review` |

OpenCode also provides `brainstorm` and `thorough-plan` primary agents. After
selecting `brainstorm`, confirm the active model in `/models`: selecting a primary
agent by ID can leave the session model unchanged.

## Permission limits

Report-only instructions apply to the agents; enforcement differs by harness:

- OpenCode agents deny file edits and ask before shell commands. Subagents also
  deny questions and further delegation. The `git-commit` agent allows only the
  exact Git commands listed in its renderer without approval; other forms,
  flags, and redirects require approval.
- Claude reviewers have read/search tools, and `docs-fetcher` has web tools.
  `git-commit` also has Bash, which its frontmatter cannot restrict by command.
- Codex agents inherit the parent's sandbox and approval policy. Their config
  files do not establish a narrower permission boundary; report-only behavior
  also relies on their instructions.

OpenCode's global config asks before access outside the project and preserves
native read and shell defaults. Native reads ask for `.env` and `.env.*`, with
`.env.example` allowed. Permissions are ordered: any agent-specific `read "*"`
allowance must be followed by sensitive-file `ask` rules and then the example-file
allowance. See the [V2 permissions documentation](https://opencode.ai/v2/docs/permissions/).

## Checks

```bash
python3 -m unittest discover -s tests
```

Tests use temporary repositories and isolated home directories. Build checks cover
agent metadata, model references, includes, TOML, and duplicate agent paths before
replacing output. Generated YAML and skill metadata are not validated for harness
requirements; permission tests model OpenCode rules locally rather than testing
live enforcement.
