# AI harness configs

Personal agents, skills, and instructions for Codex, Claude Code, and OpenCode.
Edit shared source files, then build and install them for the harnesses you use.

Requires Python 3.11+ and OpenCode V2 for OpenCode output.
There are no third-party Python dependencies.

## Install

Run the picker, or name the harnesses to install:

```bash
./install.py                 # Interactive harness, local-context, and repository setup
./install.py codex claude    # Install selected harnesses
./install.py --all           # Install all three
./install.py codex --init-local  # Also create an optional machine-local context template
```

With no arguments, the installer asks which harnesses to install, whether to
create `local.md` (default: no), and which repository URL or path to clone (blank:
skip). Explicit harness names or options do not trigger these extra setup prompts.

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

`THIRD_PARTY_NOTICES.md` is installed beside each harness's base instructions:
`~/.codex/THIRD_PARTY_NOTICES.md`, `~/.claude/THIRD_PARTY_NOTICES.md`, and
`~/.config/opencode/THIRD_PARTY_NOTICES.md`. It carries the full notices for
adapted agents and shared prompts without adding license text to model prompts.
Skill licenses remain beside their `SKILL.md` files.

If previously installed, move retired `explore` and `sidebar` agents and the
`implementation-workflow` skill out of these directories. Preserve any local
changes you want to keep. The repository no longer generates custom commands;
older installed commands are also left alone.

The `code-maintainability` agent replaces `code-readability`, `code-redundancy`,
and `code-simplifier`. The installer moves installed copies of those three to
its backup folder.

The shared planning skill is now `thorough-plan`. If previously installed,
move the old `mode-thorough-plan` skill folders and OpenCode's retired
`~/.config/opencode/agents/thorough-plan.md` out of their installation directories,
preserving local changes. The installer leaves retired entries alone.

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

Each build replaces `build/` with output for the selected harnesses. Each
`build/<harness>/` includes an unchanged copy of root `THIRD_PARTY_NOTICES.md`
beside its base instructions. Keep this file with redistributed configurations.
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

### Credit adapted material

When an agent, prompt, or skill adapts upstream material, link the upstream
source pinned to a commit and keep its license notice in this repository,
outside the text sent to the model:

- Skills: copy the upstream `LICENSE` file unchanged beside `SKILL.md`, and add
  the skill to the table in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
- Agents and shared prompts: these are single files, so put the upstream link,
  copyright line, and license text in `THIRD_PARTY_NOTICES.md`. Keep license text
  out of the file itself; an agent may carry a short attribution that points
  there.

To see which adapted upstream files changed after their pins, run:

```bash
GH_TOKEN="$(gh auth token)" ./upstream.py   # token optional; raises the API limit
./upstream.py --list                        # offline: pinned files and where they are cited
```

The script reads pins from the links above, compares each file's content at the
pin with the upstream default branch, and lists the upstream commits and a review
command for each change. It never edits pins: decide whether to adopt the change,
then update every link to the same commit. Exit status is 0 when nothing changed,
1 when a file changed or disappeared upstream, and 2 when a link is broken or one
file has different pins.

### Models and harness settings

Agent model profiles refer to entries in `source/models.toml`. Each profile has
`codex`, `claude`, and `opencode` model IDs for its targets. Optional `*_work`
values apply with `--work`, falling back to the normal value when omitted.
OpenCode model IDs include their reasoning variant, such as `#high`.

For native settings, edit `render_codex`, `render_claude`, or `render_opencode`
in `renderers.py`. Each function keeps its defaults and named exceptions together.
A new primary mode needs a renderer case and a shared agent definition.

Agent instructions can include shared fragments from `source/prompts/`:

```text
{{include:_report-only-intro.md}}
```

## Use skills and modes

Browse [source/skills](source/skills) for the available workflows, including
brainstorming, planning, code review, debugging, Git tasks, and pull requests.

The `code-maintainability` agent and shared coding instructions adapt selected
practices from the [Ponytail skill](https://github.com/DietrichGebert/ponytail/blob/df9e89941d50419fd5bcf1de41e28097f1db49b2/skills/ponytail/SKILL.md):
inspect affected code, prefer compatible reuse, and preserve safeguards. Its MIT
notice is in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). The agent
reports recommendations; the parent handles implementation and verification.

A full review runs four specialists: `code-correctness`, `code-security`,
`code-performance`, and `code-maintainability`. `code-correctness` looks for
defects from a context that did not write the change; the parent keeps
integration and the final judgment.

The optional `code-blast-radius` reviewer traces indirect effects on consumers,
interfaces, configuration, dependencies, timing, and persisted or wire data.
Ask `code-review` for a targeted blast-radius pass, especially for API/schema
changes, shared libraries, or migrations. It is not part of the four-specialist
full review. This agent only inspects and reports: it separates
confirmed risks, investigated and cleared cases, and unresolved assumptions,
then recommends checks or remedies for the parent to execute.

It adapts selected ideas from Cursor's
[pstack blast-radius skill](https://github.com/cursor/plugins/blob/df581122cde17e6e27686b5a448bde23e4ad4318/pstack/skills/blast-radius/SKILL.md);
the upstream MIT notice is in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
The agent uses the same model profile and harness defaults as `code-maintainability`;
the permission limits below still apply.

Commit implementation changes as you go in logical units. Keep local
commits lightweight and use focused checks during implementation when warranted,
with broader relevant validation at PR readiness.
Reuse valid local or CI results instead of repeating checks for each commit or
push. Inspection can be sufficient for small documentation or other low-impact edits.

| Harness | Example |
|---|---|
| Codex | `$code-review` |
| Claude Code | `/code-review` |
| OpenCode | Load `@code-review` |

Use the `thorough-plan` skill for detailed read-only planning in any harness.
OpenCode also provides a `brainstorm` primary agent. After
selecting `brainstorm`, confirm the active model in `/models`: selecting a primary
agent by ID can leave the session model unchanged.

### Project context

For substantial work that needs continuity, the `project-context` skill reuses
existing issues, PRs, or project records. When a local handoff file is needed, use
one rolling `CONTEXT.md` at the project root or an existing equivalent. Keep active
goals, important decisions, status, verification, and next actions concise.

Update the record at meaningful handoffs. At completion, cancellation, or
supersession, preserve lasting information in existing issues, PRs, or documentation
before pruning obsolete progress. Retain unrelated active work and unresolved
risks. When nothing remains active, leave `No active work` and useful pointers.
Avoid documents per feature or session and separate context archives.

We adapt selected practices from [GitHub Spec Kit](https://github.com/github/spec-kit):
observable acceptance criteria, linked tasks, and verification evidence. The
optional [detailed feature outline](source/skills/thorough-plan/feature-record.md)
is for complex work; small changes can stay in chat. Read-only planning presents
proposed records in the response; saving or cleaning them requires writing
authorization. Spec Kit is not a dependency; see the
[design rationale and sources](docs/feature-context.md).

### Machine-local context

Shared base instructions consult `~/.config/ai-agents/local.md` when it exists
and is readable. If it is absent or inaccessible, agents continue normally without
a missing-configuration notice. Work machines can omit it or use it for approved
work context; no personal wiki is assumed.

To create an optional neutral template while installing:

```bash
./install.py codex --init-local
```

The new file is created with mode `600`. Existing files, directories, and symlinks
are preserved, even with `--force`. Normal installation leaves this file alone.
Without a cloned wiki, the template contains a heading and plain Markdown setup
guidance, with no active knowledge pointer. To also clone a repository, use your
existing Git SSH/HTTPS authentication:

```bash
./install.py codex --init-local --clone-repo git@github.com:OWNER/REPOSITORY.git
```

`--clone-repo` accepts a Git URL, SSH repository address, or local repository path.
It clones into `~/Knowledge/<repo-name>/`, stripping a trailing `.git`.
Local paths such as `.` and `/path/to/wiki/.` use the resolved directory name.
Build validation completes before cloning, so invalid build options leave no clone.
It refuses an existing destination, including a symlink, even with `--force`;
there is no automatic pull, reset, or replacement. A failed clone still initializes
`local.md` when `--init-local` is selected, pointing to the requested repository's
`AGENTS.md` at its intended checkout location. Agents report an unavailable checkout
or entry point and continue without it. The installer stops harness installation
and returns an error; inspect any remaining clone destination before retrying.
It does not move an existing checkout. Git is required only when this option is used.

Existing checkouts under `~/.config/ai-agents/<repo-name>/` are not moved or
deleted. To relocate one, move the complete checkout, including `.git` and any
uncommitted work, to `~/Knowledge/<repo-name>/` when no session is using it.
Then update its pointer in `~/.config/ai-agents/local.md` and any saved
project/workspace paths or filesystem permissions. The installer preserves
existing local context, so rerunning `--init-local` will not rewrite an old pointer.

If an earlier setup keeps its knowledge pointer in `~/.config/ai-agents/shared-knowledge.md`,
copy the approved pointer into `local.md` before reinstalling. The installer does
not migrate that file, and the new shared instructions consult only `local.md`.

The flags are independent: cloning alone does not create `local.md`. Combining
both flags creates a pointer to `~/Knowledge/<repo-name>/AGENTS.md` in a **new**
`local.md` from the requested repository name, even if cloning fails or the entry
point is not yet present. With no repository specified, `--init-local` creates the
neutral template. Always use `AGENTS.md` as a knowledge repository's entry point.
Existing local context is preserved; update its pointer locally to the repository's
`AGENTS.md` when needed. Edit it locally as needed:

```markdown
# Machine-local context

## Shared knowledge

For shared knowledge, read `~/Knowledge/<repo-name>/AGENTS.md`.
Use its selective retrieval and pending-correction guidance.
Keep capture and curation writes in the dedicated knowledge project.
Report unavailable or stale configured knowledge.
Do not broaden sandbox access for retrieval.
This file grants no synchronization or publishing permission.
```

Replace `<repo-name>` with the actual checkout directory name; it is not a literal
folder name. `--init-local` alone does not clone a repository.
Keep private locations and content out of public repos. Configure each host
separately and test fresh-session retrieval with its actual permissions. Wiki access and synchronization require separate configuration.

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
