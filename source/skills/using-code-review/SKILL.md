---
name: using-code-review
description: How and when to invoke code review agents (@code-security, @code-readability, @code-performance, @code-redundancy, @code-simplifier, @code-full-review). Use before major PRs, audits, refactors, or whenever targeted review feedback is needed.
---

# Using Code Review Agents

This skill explains when and how to use the specialized code review agents.

## Available Review Agents

### @code-security
**Purpose**: Security vulnerability detection and OWASP compliance checks

**When to use**:
- Before commits touching authentication or authorization
- When handling user input or file uploads
- Before deploying public-facing endpoints
- Regular security audits
- When adding new dependencies

**What it checks**:
- OWASP Top 10 vulnerabilities
- SQL injection, XSS, CSRF risks
- Insecure cryptography and data exposure
- Authentication and authorization flaws
- Security misconfigurations

### @code-readability
**Purpose**: Code clarity, naming conventions, and documentation review

**When to use**:
- Before major pull requests
- When onboarding new team members to a codebase
- Reviewing legacy code for maintainability
- When code is hard to understand
- Ensuring consistent style across the project

**What it checks**:
- Clear and descriptive naming
- Code structure and organization
- Documentation quality
- Consistent formatting
- Appropriate comments

### @code-performance
**Purpose**: Performance bottleneck identification and optimization recommendations

**When to use**:
- When profiling reveals slow code paths
- Before scaling features to production
- Optimizing database queries or API calls
- When response times are too slow
- Memory usage concerns

**What it checks**:
- Algorithm efficiency
- Database query optimization
- Memory leaks
- I/O bottlenecks
- Concurrency issues

### @code-redundancy
**Purpose**: Duplicate code detection and DRY principle violations

**When to use**:
- Before large refactoring efforts
- When codebase feels bloated
- Finding opportunities for shared utilities
- Identifying copy-paste code
- Reducing maintenance burden

**What it checks**:
- Duplicate code blocks
- Repeated patterns
- Unused code and dead imports
- Opportunities for abstraction
- Similar functions that could be unified

### @code-simplifier
**Purpose**: Complexity reduction and code simplification

**When to use**:
- When code is hard to understand
- High cyclomatic complexity
- Deep nesting or long functions
- Overly clever or compact code
- After reviewing readability issues

**What it checks**:
- Unnecessary complexity
- Nested ternaries and conditionals
- Long functions that should be split
- Magic numbers and unclear expressions
- Opportunities for early returns

### @code-full-review
**Purpose**: Comprehensive review orchestrating all 5 specialist agents

**When to use**:
- Major pull requests before merging
- Pre-release code audits
- When you want feedback from all perspectives
- Thorough review of critical components
- Before handing off code to another team

**What it does**:
- Runs all 5 review agents in parallel
- Aggregates findings from each specialist
- Provides comprehensive feedback
- Prioritizes issues by severity

## Usage Patterns

All review agents operate in **report-only mode** - they analyze and return findings without asking questions or applying changes directly.

### Single Agent Workflow

```
1. Invoke the agent: @code-security src/auth.js
2. Wait for the security report
3. Review findings and decide which to address
4. Apply approved fixes
5. Re-run agent to verify fixes
```

### Full Review Workflow

```
1. Invoke: @code-full-review src/
2. Receive reports from all 5 agents
3. Prioritize findings (security > performance > readability)
4. Address high-priority issues first
5. Iterate on medium/low priority items
```

## Cross-Referencing with Skills

Review agents work best when combined with relevant skills:

- **For implementation**: Use `implementation-workflow` for overall development methodology
- **For commits**: Use `git-workflows` for commit message and PR best practices

## Agent Permissions

All code review agents have these permissions set:
- `edit: deny` - They suggest changes but don't apply them
- `bash: deny` - They don't execute commands
- `question: deny` - They return reports without user interaction

This ensures they operate as analysis tools that return structured findings to the calling agent or user.

## When NOT to Use Review Agents

- **Don't use** for simple, obvious code where the issues are already known
- **Don't over-rely** on agents - human review is still critical
- **Don't use** as a substitute for proper testing and CI/CD
- **Don't expect** agents to catch all issues - they're assistance tools, not replacements for expertise

## Tips for Best Results

1. **Be specific**: Point agents at specific files or directories, not entire repos
2. **Iterate**: Run multiple times as you address findings
3. **Combine perspectives**: Use multiple agents for complex code
4. **Load relevant skills**: Give agents access to language-specific patterns
5. **Understand context**: Review agent findings in context of your codebase's specific needs
