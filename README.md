# AI-Agents

A collection of specialized code review agents and commands for **Claude Code** and **OpenCode**.

## What's Included

| Name | Type | Purpose |
|------|------|---------|
| `code-security` | Agent + Command | Security vulnerability detection, OWASP Top 10 compliance |
| `code-readability` | Agent + Command | Code clarity, naming, structure, documentation review |
| `code-performance` | Agent + Command | Performance bottlenecks, algorithm optimization |
| `code-full-review` | Command only | Orchestrates all 3 agents, synthesizes findings with trade-off debates |

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
│       └── AGENTS.md
├── build.sh               # Generates build/ from source/
└── install.sh             # Installs to ~/.claude and ~/.config/opencode
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
./install.sh --claude-only   # Only install Claude Code
./install.sh --opencode-only # Only install OpenCode
./install.sh --skip-build    # Use existing build/ (skip regeneration)
```

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

**Commands**:
```
/code-security src/auth/login.ts
/code-readability src/utils/
/code-performance src/data-processor.ts
/code-full-review src/api/
```

**Agents** (via @ mentions):
```
@code-security review this file for vulnerabilities
@code-readability check naming conventions
@code-performance find bottlenecks
```

## Customization

### Editing Instructions

All agent/command logic lives in `source/prompts/`. Edit these files to customize behavior, then run `./install.sh` to rebuild and reinstall.

Each prompt file uses **combined frontmatter**:

```yaml
---
description: What this agent does...
type: agent+command    # or "command-only"
claude:
  tools: Read, Glob, Grep
  model: opus
opencode:
  mode: subagent
  model: anthropic/claude-opus-4-20250514
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
- `build/opencode/AGENTS.md` - From `base-instructions.md`

### Agent vs Command

| Type | Claude Code | OpenCode |
|------|-------------|----------|
| Agent | Auto-invoked when relevant | Called via `@agent-name` |
| Command | Manual via `/command-name` | Manual via `/command-name` |

Commands with type `agent+command` create both. Commands with type `command-only` create only commands (like `code-full-review` which orchestrates sub-agents).

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
