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

## Deployment

### Option 1: Global (All Projects)

Copy to your home directory for use across all projects:

```bash
# Copy agents (available globally)
cp -r claude/agents/* ~/.claude/agents/

# Copy commands (available globally)
cp -r claude/commands/* ~/.claude/commands/

# Copy prompts (required for agents/commands to work)
mkdir -p ~/.claude/prompts
cp -r claude/prompts/* ~/.claude/prompts/

# Optionally copy CLAUDE.md for global instructions
cp claude/CLAUDE.md ~/.claude/CLAUDE.md
```

### Option 2: Project-Level (Single Project)

Copy the `claude` folder to your project root and rename it to `.claude`:

```bash
# From this repo
cp -r claude /path/to/your/project/.claude
```

Or using git:
```bash
# Clone directly into your project
cd /path/to/your/project
git clone https://github.com/YOUR_USERNAME/AI-Agents.git .claude-temp
mv .claude-temp/claude .claude
rm -rf .claude-temp
```

### Option 3: Symlink (Stay Updated)

Symlink to this repo so updates are automatic:

```bash
# From the root of this repo, symlink to global config
ln -s "$(pwd)/claude/agents/"* ~/.claude/agents/
ln -s "$(pwd)/claude/commands/"* ~/.claude/commands/
ln -s "$(pwd)/claude/prompts" ~/.claude/prompts
ln -s "$(pwd)/claude/CLAUDE.md" ~/.claude/CLAUDE.md
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
