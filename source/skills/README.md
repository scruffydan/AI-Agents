# Skills Directory

This directory contains **modular procedural knowledge** that agents can reference. Skills are separate from agent instructions to improve maintainability and reduce token usage.

## What Are Skills?

Skills are reusable knowledge modules that contain:
- Technical checklists and best practices
- Step-by-step workflows and methodologies
- Language-specific security patterns
- Tool usage guides

## Skills vs Instructions vs Agents

| Concept | Purpose | Location | Example |
|---------|---------|----------|---------|
| **Instructions** | Core identity & behavior | `prompts/base-instructions.md` | "You are a Principal Engineer" |
| **Skills** | Procedural knowledge | `skills/*.md` | "JavaScript security checklist" |
| **Agents** | Task-specific personas | `prompts/*.md` | `@code-security`, `@explore` |

## Current Skills

### Security Skills
- **javascript-security.md** - JS/TypeScript security best practices
- **python-security.md** - Python security patterns and dangerous functions
- **go-security.md** - Go security patterns, templates, crypto
- **shell-security.md** - Bash security, quoting, command injection prevention
- **sql-security.md** - SQL injection prevention, parameterized queries

### Workflow Skills
- **implementation-workflow.md** - 6-phase implementation methodology
- **git-workflows.md** - Git best practices, commits, branching
- **using-docs-fetcher.md** - How to use @docs-fetcher agent

## How Skills Are Used

Agents reference skills using relative paths:

```markdown
For JavaScript security guidelines, see `skill/javascript-security.md`
```

After building, skills are available at:
- Claude: `~/.claude/skills/`
- OpenCode: `~/.config/opencode/skill/`

## Adding New Skills

1. Create a new `.md` file in this directory
2. Write clear, focused procedural knowledge
3. Reference it from relevant agent files
4. Run `./build.sh` to copy to build directories

### Skill Format

Skills should be:
- **Focused** - Cover one specific domain
- **Actionable** - Provide concrete steps or checklists
- **Reusable** - Referenced by multiple agents
- **Maintainable** - Easy to update independently

Example:
```markdown
# Skill Name

Brief description of what this skill covers.

## Section 1
Content...

## Section 2
Content...
```

## Benefits

1. **Modularity** - Update knowledge without touching agent definitions
2. **Reduced Bloat** - Keep agent prompts focused on behavior
3. **Reusability** - Multiple agents can share the same skill
4. **Easier Maintenance** - Update best practices in one place

## Future Enhancements

- Skill auto-loading based on file types
- Skill versioning for reproducibility
- Community-contributed skill library
