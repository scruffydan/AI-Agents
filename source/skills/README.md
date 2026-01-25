# Skills Directory

Modular procedural knowledge following the [Agent Skills standard](https://github.com/anthropics/anthropic-sdk-typescript/tree/main/agents-api). Agents load skills on-demand to reduce token usage.

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

## Available Skills (9 total)

**Security** (language-specific):
- `javascript-security` - JS/TS security patterns
- `python-security` - Python dangerous functions, injection prevention
- `go-security` - Go templates, crypto, race conditions
- `shell-security` - POSIX sh security (portable sh/bash/dash/ash)
- `sql-security` - SQL injection prevention

**Workflow**:
- `implementation-workflow` - 6-phase development methodology
- `git-workflows` - Git best practices

**Usage Guides**:
- `using-docs-fetcher` - When/how to use `@docs-fetcher`
- `using-code-review` - Using all 5 code review agents

## Usage

Agents reference skills for dynamic loading:

```markdown
When reviewing JavaScript, load skill `javascript-security` for security patterns.
```

For format details, see [Agent Skills documentation](https://github.com/anthropics/anthropic-sdk-typescript/tree/main/agents-api).

## Adding Skills

1. Create `source/skills/my-skill/SKILL.md` following the [Agent Skills format](https://github.com/anthropics/anthropic-sdk-typescript/tree/main/agents-api)
2. Reference from agents: `Load skill \`my-skill\` when...`
3. Run `./install.sh`

## Guidelines

Skills should be:
- **Focused** - One specific domain
- **Actionable** - Concrete checklists/patterns
- **Reusable** - Used by multiple agents
- **Standards-compliant** - Follow [Agent Skills format](https://github.com/anthropics/anthropic-sdk-typescript/tree/main/agents-api)

## Benefits

- **On-demand loading** - Skills loaded only when needed
- **Modularity** - Update knowledge independently
- **Reusability** - Shared across agents
- **Cross-references** - Skills ↔ Agents ↔ Workflows create a knowledge graph
