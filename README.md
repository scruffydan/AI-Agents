# AI-Agents

A collection of specialized agents, commands, and modes for **Claude Code** and **OpenCode**.

## What's Included

| Name | Type | Purpose |
|------|------|---------|
| `code-security` | Subagent | Security vulnerability detection, OWASP Top 10 compliance |
| `code-readability` | Subagent | Code clarity, naming, structure, documentation review |
| `code-performance` | Subagent | Performance bottlenecks, algorithm optimization |
| `code-redundancy` | Subagent | Duplicate code, repeated patterns, DRY improvements |
| `code-simplifier` | Subagent | Simplifies code for clarity, consistency, and maintainability |
| `code-full-review` | Command | Orchestrates all review agents, synthesizes findings with trade-off debates |
| `explore` | Subagent | Codebase exploration, file search, dependency tracing |
| `docs-fetcher` | Subagent | Fetch and extract relevant documentation from URLs |
| `git-commit` | Subagent | Analyzes git history, drafts commit message for user verification |
| `sidebar` | Subagent | Answer general questions unrelated to coding session |
| `brainstorm` | Mode (OpenCode only) | High-temperature creative mode for generating diverse ideas |
| `thorough-plan` | Mode (OpenCode only) | Planning mode that asks clarifying questions before proceeding |
| `five-whys` | Skill | Root cause analysis using Toyota's Five Whys technique |
| `brainstorming` | Skill | Creative ideation guidance before building |
| `implementation-workflow` | Skill | 6-phase development methodology |
| `executing-plans` | Skill | Execute pre-written plans with checkpoints |
| `git-commit` | Skill | Analyzes last 10 commits to match repo conventions |
| `git-push` | Skill | Pre-push checklist (README updates, tests, security) |
| `receiving-code-review` | Skill | Implement review feedback with verification |
| `subagent-driven-development` | Skill | Run independent tasks with subagents |
| `systematic-debugging` | Skill | Structured debugging before proposing fixes |
| `update-readme` | Skill | Reminds to update README before committing changes |
| `using-docs-fetcher` | Skill | When/how to use `@docs-fetcher` |
| `using-code-review` | Skill | Using all 5 code review agents |
| `verification-before-completion` | Skill | Verify before claiming completion |
| `writing-skills` | Skill | Author and validate skill definitions |

Some skills are sourced from [obra/superpowers](https://github.com/obra/superpowers). Skills follow the [Agent Skills standard](https://github.com/anthropics/anthropic-sdk-typescript/tree/main/agents-api).

## Requirements

- **yq** (v4) - YAML processor for build script
  ```bash
  brew install yq
  ```
- **jq** - JSON processor for work mode model mappings
  ```bash
  brew install jq
  ```

## Installation

### Quick Install

```bash
./install.sh
```

This will:
1. Run `build.sh` to generate tool-specific configs
2. Install Claude Code configs to `~/.claude/` (agents, commands, skills)
3. Install OpenCode configs to `~/.config/opencode/` (agents, commands, skills)

### Options

```bash
./install.sh -y              # Force overwrite without prompts
./install.sh --claude        # Only install Claude Code
./install.sh --opencode      # Only install OpenCode
./install.sh --chatgpt-provider opencode
                          # Use opencode for OpenCode GPT models
./install.sh --work          # Use work environment model mappings for OpenCode
./install.sh --skip-build    # Use existing build/ (skip regeneration)
```

### Model Provider Selection

By default, OpenCode GPT models are normalized to the `openai` provider. You can override that in either script, or choose interactively during `./install.sh` when OpenCode is selected:

```bash
./install.sh --opencode --chatgpt-provider openai    # Default behavior
./install.sh --opencode --chatgpt-provider opencode  # Use opencode for GPT models
./build.sh --chatgpt-provider opencode               # Build only, using opencode GPT models
```

If you use `--work`, provider selection is skipped and model mapping still happens through `source/model-mappings.json`:

```bash
./install.sh --opencode --work    # Install OpenCode with work model mappings
./build.sh --work                 # Build only, using work model mappings
```

Model mappings are configured in `source/model-mappings.json`. This allows you to map models like:
- `opencode/claude-sonnet-4-6` → `google-vertex/gemini-3.1-pro-preview`
- `opencode/gemini-3.1-pro` → `google-vertex/gemini-3.1-pro-preview`
- `opencode/gpt-5.4` → `google-vertex-anthropic/claude-opus-4-5@20251101`
- `openai/gpt-5.4` → `google-vertex/gemini-3.1-pro-preview`

Non-GPT models keep the provider defined in the prompt frontmatter. Unmapped models will show a warning during build and keep their original configured provider/model.

**Work Mode Setup Requirements:**
- Set `GOOGLE_CLOUD_PROJECT` environment variable (if using Vertex AI)
- Authenticate via `gcloud auth application-default login` or set `GOOGLE_APPLICATION_CREDENTIALS`
- Optionally set `VERTEX_LOCATION` (defaults to `global`)

### OpenCode Config (Optional)

```bash
./opencode-init.sh           # Install opencode.json with secure permission defaults
./opencode-init.sh -y        # Force overwrite without prompts
```

This installs a `opencode.json` to `~/.config/opencode/` with sensible security defaults:
- Sharing disabled
- Dangerous commands require approval (rm -rf, git push, npm install, etc.)
- Safe read-only commands allowed (ls, cat, head, tail, echo, git status, etc.)
- Sensitive files blocked (*.env, *.key, secrets, credentials, etc.)

### Manual Build Only

```bash
./build.sh                   # Just generate configs (defaults GPT models to openai)
./build.sh --chatgpt-provider opencode
                            # Generate configs with opencode GPT models
./build.sh --work            # Generate configs using work model mappings
```

## Usage

### Claude Code

**Commands** (manual):
```bash
/code-security src/auth/login.ts
/code-readability src/utils/
/code-performance src/data-processor.ts
/code-full-review src/api/
```

**Agents** (automatic):
- "Review this code for security issues" → triggers `code-security`
- "Is this code readable?" → triggers `code-readability`
- "Optimize this function" → triggers `code-performance`

### OpenCode

**Agents** (via @ mentions):
```
@code-security src/auth/login.ts
@code-readability src/utils/
@code-performance src/data-processor.ts
@git-commit                          # Analyzes changes, proposes commit message
```

**Commands**:
```
/code-full-review src/api/
```

**Modes** (switch with Tab):
```
brainstorm    # High-temperature creative mode
```

Note: In OpenCode, the individual review agents are invoked via `@` mentions. Only `code-full-review` is a slash command since it orchestrates all 5 specialist agents. Modes change the AI's behavior and are switched using the Tab key.

## Special Workflows

### Git Commit Workflow

The `@git-commit` agent provides a safe, verified commit workflow:

1. **Analyze**: The agent analyzes your git history (last 10 commits) to understand repository conventions
2. **Prepare**: Drafts a commit message that matches your repo's style and reviews staged changes
3. **Verify**: Returns the proposed commit message and file list for your approval
4. **Commit**: After you approve, the main agent runs the commit

**Example:**
```
You: @git-commit
  ↓
Agent analyzes git history and returns:
  • Proposed message: "feat(auth): add JWT validation"
  • Files: src/auth/jwt.ts, tests/auth.test.ts
  • Convention found: Uses conventional commits with scope
  ↓
You approve
  ↓
Main agent commits with approved message
```

**Benefits:**
- Keeps main context clean (analysis happens in subagent)
- Automatically matches your repository's commit style
- You verify every commit before it happens
- No accidental commits

## Customization

### Editing Instructions

All agent/command logic lives in `source/prompts/`. Edit these files to customize behavior, then run `./install.sh` to rebuild and reinstall.

Each prompt file uses **combined frontmatter**:

```yaml
---
description: What this agent does...
type: subagent    # or "command" or "mode"
claude:
  tools: Read, Glob, Grep
  model: opus
opencode:
  mode: subagent
  model: opencode/gpt-5.4
  temperature: 0.8     # For modes: controls creativity (0.0-1.0)
  tools:
    write: false
    edit: false
    bash: false
---

# Prompt content here...

$ARGUMENTS
```

The `build.sh` script parses this and generates the appropriate format for each tool.

### Adding New Agents

1. Create `source/prompts/my-agent.md` with combined frontmatter
2. Run `./install.sh` to rebuild and install

### Adding New Skills

1. Create `source/skills/my-skill/SKILL.md` following the [Agent Skills format](https://github.com/anthropics/anthropic-sdk-typescript/tree/main/agents-api)
2. Reference from agents: `Load skill \`my-skill\` when...`
3. Run `./install.sh`

### Base Instructions

`source/prompts/AGENTS.md` generates:
- Claude Code: `~/.claude/CLAUDE.md` (global instructions)
- OpenCode: `~/.config/opencode/AGENTS.md` (global instructions)

## How It Works

### Build Process

`build.sh` reads each prompt in `source/prompts/` and generates:

**For Claude Code:**
- `build/claude/agents/{name}.md` - Agent with Claude-specific frontmatter
- `build/claude/commands/{name}.md` - Raw prompt for slash commands
- `build/claude/skills/{name}/SKILL.md` - Skills (copied from `source/skills/`)
- `build/claude/CLAUDE.md` - From `AGENTS.md`

**For OpenCode:**
- `build/opencode/agent/{name}.md` - Agent with OpenCode-specific frontmatter
- `build/opencode/command/{name}.md` - Command that references the agent
- `build/opencode/mode/{name}.md` - Mode with temperature and tool settings
- `build/opencode/skill/{name}/SKILL.md` - Skills (copied from `source/skills/`)
- `build/opencode/AGENTS.md` - From `AGENTS.md`

### Agent vs Command vs Mode

| Type | Claude Code | OpenCode |
|------|-------------|----------|
| Agent | Auto-invoked when relevant | Called via `@agent-name` |
| Command | Manual via `/command-name` | Manual via `/command-name` |
| Mode | N/A | Switch via Tab key, changes behavior |

Prompts with type `subagent` create both Claude agents and OpenCode agents. Prompts with type `command` create commands only (like `code-full-review` which orchestrates sub-agents). Prompts with type `mode` create OpenCode modes only (like `brainstorm` for creative exploration).

## Workflow

All review agents use a hybrid workflow:

1. **Analyze** - Read target files and identify issues
2. **Report** - Present findings with severity and recommendations
3. **Get Approval** - Ask user which fixes to apply
4. **Apply Fixes** - Only after user approval

The `code-full-review` command:
1. Spawns all review specialists in parallel
2. Collects their findings
3. Presents debates where recommendations conflict
4. Helps user make informed trade-off decisions

## License

MIT
