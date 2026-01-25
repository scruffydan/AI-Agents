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
| `sidebar` | Subagent | Answer general questions unrelated to coding session |
| `brainstorm` | Mode (OpenCode only) | High-temperature creative mode for generating diverse ideas |
| `thorough-plan` | Mode (OpenCode only) | Planning mode that asks clarifying questions before proceeding |
| **Security** | **Skill Group** | Language-specific secure coding guidance |
| `javascript-security` | Skill | JS/TS security patterns |
| `python-security` | Skill | Python dangerous functions, injection prevention |
| `go-security` | Skill | Go templates, crypto, race conditions |
| `shell-security` | Skill | POSIX sh security (portable sh/bash/dash/ash) |
| `sql-security` | Skill | SQL injection prevention |
| **Workflow** | **Skill Group** | Planning, execution, and delivery discipline |
| `brainstorming` | Skill | Creative ideation guidance before building |
| `implementation-workflow` | Skill | 6-phase development methodology |
| `executing-plans` | Skill | Execute pre-written plans with checkpoints |
| `git-commit` | Skill | Analyzes last 10 commits to match repo conventions |
| `git-push` | Skill | Pre-push checklist (README updates, tests, security) |
| `receiving-code-review` | Skill | Implement review feedback with verification |
| `subagent-driven-development` | Skill | Run independent tasks with subagents |
| `systematic-debugging` | Skill | Structured debugging before proposing fixes |
| **Guides** | **Skill Group** | How-to references for other tools |
| `using-docs-fetcher` | Skill | When/how to use `@docs-fetcher` |
| `using-code-review` | Skill | Using all 5 code review agents |
| `verification-before-completion` | Skill | Verify before claiming completion |
| `writing-skills` | Skill | Author and validate skill definitions |

Some skills are sourced from [obra/superpowers](https://github.com/obra/superpowers). Skills follow the [Agent Skills standard](https://github.com/anthropics/anthropic-sdk-typescript/tree/main/agents-api).

## Directory Structure

```
AI-Agents/
├── source/
│   ├── prompts/       # Agent/command definitions (combined frontmatter)
│   └── skills/        # Modular procedural knowledge (Agent Skills standard)
├── build/             # GITIGNORED - generated output for claude/ and opencode/
├── build.sh           # Generates build/ from source/
├── install.sh         # Installs to ~/.claude and ~/.config/opencode
└── opencode-init.sh   # Installs opencode.json config with secure defaults
```

## Requirements

- **yq** (v4) - YAML processor for build script
  ```bash
  brew install yq
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
./install.sh --vertex        # Use Google Vertex AI as the model provider for OpenCode
./install.sh --skip-build    # Use existing build/ (skip regeneration)
```

### Model Provider Selection

By default, OpenCode agents use the `opencode` provider (OpenCode Zen). You can alternatively use **Google Vertex AI** for Anthropic and Gemini models:

```bash
./install.sh --opencode --vertex    # Install OpenCode with Vertex AI models
./build.sh --vertex                 # Build only, using Vertex AI models
```

This changes model strings from `opencode/claude-sonnet-4-5` to `google-vertex-anthropic/claude-sonnet-4-5@20250929`, and `opencode/gemini-3-pro` to `google-vertex/gemini-3-pro-preview`.

**Vertex AI Setup Requirements:**
- Set `GOOGLE_CLOUD_PROJECT` environment variable
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
./build.sh                   # Just generate configs (uses OpenCode provider)
./build.sh --vertex          # Generate configs using Vertex AI provider
./build.sh --opencode        # Explicitly use OpenCode provider (default)
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
```

**Commands**:
```
/code-full-review src/api/
```

**Modes** (switch with Tab):
```
brainstorm    # High-temperature creative mode
```

Note: In OpenCode, the individual review agents are invoked via `@` mentions. Only `code-full-review` is a slash command since it orchestrates all 3 agents. Modes change the AI's behavior and are switched using the Tab key.

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
  model: anthropic/claude-opus-4
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
