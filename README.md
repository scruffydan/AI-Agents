# AI-Agents

A collection of specialized code review agents and commands for **Claude Code** and **OpenCode**.

## What's Included

| Name | Type | Purpose |
|------|------|---------|
| `code-security` | Agent only | Security vulnerability detection, OWASP Top 10 compliance |
| `code-readability` | Agent only | Code clarity, naming, structure, documentation review |
| `code-performance` | Agent only | Performance bottlenecks, algorithm optimization |
| `code-full-review` | Command only | Orchestrates all 3 agents, synthesizes findings with trade-off debates |
| `brainstorm` | Mode (OpenCode) / Command (Claude) | High-temperature creative mode for generating diverse ideas |

## Directory Structure

```
AI-Agents/
├── source/prompts/        # Source of truth (combined frontmatter)
│   ├── base-instructions.md
│   ├── code-security.md
│   ├── code-readability.md
│   ├── code-performance.md
│   └── code-full-review.md
├── build/                 # GITIGNORED - generated output
│   ├── claude/
│   │   ├── agents/
│   │   ├── commands/
│   │   └── CLAUDE.md
│   └── opencode/
│       ├── agent/
│       ├── command/
│       ├── mode/
│       └── AGENTS.md
├── build.sh               # Generates build/ from source/
├── install.sh             # Installs to ~/.claude and ~/.config/opencode
└── opencode-init.sh       # Installs opencode.json config with secure defaults
```

## Installation

### Quick Install

```bash
./install.sh
```

This will:
1. Run `build.sh` to generate tool-specific configs
2. Install Claude Code configs to `~/.claude/`
3. Install OpenCode configs to `~/.config/opencode/`

### Options

```bash
./install.sh -y              # Force overwrite without prompts
./install.sh --claude        # Only install Claude Code
./install.sh --opencode      # Only install OpenCode
./install.sh --skip-build    # Use existing build/ (skip regeneration)
```

### OpenCode Config (Optional)

```bash
./opencode-init.sh           # Install opencode.json with secure permission defaults
./opencode-init.sh -y        # Force overwrite without prompts
```

This installs a `opencode.json` to `~/.config/opencode/` with sensible security defaults (sharing disabled, dangerous commands require approval, etc.).

### Manual Build Only

```bash
./build.sh                   # Just generate configs without installing
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
type: agent+command    # or "agent-only", "command-only", or "mode-only"
claude:
  tools: Read, Glob, Grep
  model: opus
opencode:
  mode: subagent
  model: anthropic/claude-opus-4-20250514
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

### Base Instructions

`source/prompts/base-instructions.md` generates:
- Claude Code: `~/.claude/CLAUDE.md` (global instructions)
- OpenCode: `~/.config/opencode/AGENTS.md` (global instructions)

## How It Works

### Build Process

`build.sh` reads each prompt in `source/prompts/` and generates:

**For Claude Code:**
- `build/claude/agents/{name}.md` - Agent with Claude-specific frontmatter
- `build/claude/commands/{name}.md` - Raw prompt for slash commands
- `build/claude/CLAUDE.md` - From `base-instructions.md`

**For OpenCode:**
- `build/opencode/agent/{name}.md` - Agent with OpenCode-specific frontmatter
- `build/opencode/command/{name}.md` - Command that references the agent
- `build/opencode/mode/{name}.md` - Mode with temperature and tool settings
- `build/opencode/AGENTS.md` - From `base-instructions.md`

### Agent vs Command vs Mode

| Type | Claude Code | OpenCode |
|------|-------------|----------|
| Agent | Auto-invoked when relevant | Called via `@agent-name` |
| Command | Manual via `/command-name` | Manual via `/command-name` |
| Mode | N/A | Switch via Tab key, changes behavior |

Commands with type `agent+command` create both. Commands with type `command-only` create only commands (like `code-full-review` which orchestrates sub-agents). Commands with type `mode-only` create OpenCode modes only (like `brainstorm` for creative exploration).

## Workflow

All review agents use a hybrid workflow:

1. **Analyze** - Read target files and identify issues
2. **Report** - Present findings with severity and recommendations
3. **Get Approval** - Ask user which fixes to apply
4. **Apply Fixes** - Only after user approval

The `code-full-review` command:
1. Spawns all 3 specialists in parallel
2. Collects their findings
3. Presents debates where recommendations conflict
4. Helps user make informed trade-off decisions

## License

MIT
