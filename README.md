# Claude Code AI Agents

A collection of specialized code review agents and commands for Claude Code.

## What's Included

| Name | Type | Purpose |
|------|------|---------|
| `code-security` | Agent + Command | Security vulnerability detection, OWASP Top 10 compliance |
| `code-readability` | Agent + Command | Code clarity, naming, structure, documentation review |
| `code-performance` | Agent + Command | Performance bottlenecks, algorithm optimization |
| `code-full-review` | Command only | Spawns all 3 agents in parallel, synthesizes trade-offs |

## Directory Structure

```
claude/
├── CLAUDE.md          # Base instructions for Claude
├── agents/            # Auto-invoked agents (Claude decides when to use)
├── commands/          # Manual slash commands (/code-security, etc.)
└── prompts/           # Shared instructions (source of truth)
```

## Installation

### Quick Install (Recommended)

Run the install script to copy all files to your global config:

```bash
./install.sh
```

This copies all agents, commands, prompts, and CLAUDE.md to `~/.claude/` for use across all projects. Run it again to update when pulling new changes.

### Project-Level Install

Copy the `claude` folder to your project root and rename it to `.claude`:

```bash
# From this repo
cp -r claude /path/to/your/project/.claude
```

Or clone directly into your project:
```bash
cd /path/to/your/project
git clone https://github.com/YOUR_USERNAME/AI-Agents.git .claude-temp
mv .claude-temp/claude .claude
rm -rf .claude-temp
```

## Usage

### Slash Commands (Manual)

Invoke manually with a file or directory as argument:

```bash
/code-security src/auth/login.ts
/code-readability src/utils/
/code-performance src/data-processor.ts
/code-full-review src/api/
```

### Agents (Automatic)

Claude will automatically invoke these agents when relevant. For example:
- "Review this code for security issues" → triggers `code-security` agent
- "Is this code readable?" → triggers `code-readability` agent
- "Optimize this function" → triggers `code-performance` agent

Note: `code-full-review` is command-only (`/code-full-review`) - it spawns the 3 specialist agents in parallel.

## Customization

### Editing Instructions

All agent/command logic lives in `prompts/`. Edit these files to customize behavior:

- `prompts/code-security.md` - Security review criteria
- `prompts/code-readability.md` - Readability standards
- `prompts/code-performance.md` - Performance guidelines
- `prompts/code-full-review.md` - Orchestration logic

Changes apply to both agents and commands automatically.

### Adding New Agents

1. Create the prompt in `prompts/my-agent.md`
2. Create the agent wrapper in `agents/my-agent.md`:
   ```markdown
   ---
   name: my-agent
   description: When this agent should be invoked
   tools: Read, Glob, Grep
   ---

   Read and apply the instructions from `.claude/prompts/my-agent.md`.

   $ARGUMENTS
   ```
3. Create the command wrapper in `commands/my-agent.md`:
   ```markdown
   Read and apply the instructions from `.claude/prompts/my-agent.md`.

   $ARGUMENTS
   ```

### Available Tools for Agents

| Tool | Purpose |
|------|---------|
| `Read` | Read file contents |
| `Write` | Create/overwrite files |
| `Edit` | Modify existing files |
| `Glob` | Find files by pattern |
| `Grep` | Search file contents |
| `Bash` | Run shell commands |

Read-only agents (reviewers) should use: `Read, Glob, Grep`
Write agents (fixers) should add: `Write, Edit, Bash`

## Precedence

Claude Code loads instructions in this order (later overrides earlier):

1. `~/.claude/CLAUDE.md` (global)
2. `.claude/CLAUDE.md` (project)
3. `CLAUDE.md` (project root)
4. `claude.md` (project root)

## License

MIT
