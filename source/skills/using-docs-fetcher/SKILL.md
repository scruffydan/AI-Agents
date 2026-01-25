---
name: using-docs-fetcher
description: How to use @docs-fetcher to pull current, targeted external documentation (APIs, SDKs, configs, errors, version changes). Use when you need authoritative docs or examples instead of relying on memory.
---

# Using the Documentation Fetcher

When you need to look up external documentation (APIs, libraries, frameworks, configuration options, or any technical reference), use the `@docs-fetcher` agent to fetch and extract only the relevant portions. This keeps the main context clean and avoids flooding it with entire documentation pages.

## When to Use @docs-fetcher

Use the docs-fetcher agent when you need to:

- **Look up API methods, endpoints, or parameters** - Understanding how to call specific APIs or what parameters are available
- **Check configuration options for libraries/frameworks** - Finding available config settings and their expected values
- **Find code examples for specific use cases** - Locating official examples that demonstrate best practices
- **Research version-specific features or breaking changes** - Understanding what changed between versions
- **Troubleshoot errors with official documentation** - Finding solutions to error messages or unexpected behavior

## How to Use @docs-fetcher

### Basic Pattern

```
@docs-fetcher: Fetch the Stripe Payment Intents API documentation,
specifically how to create a payment intent with metadata.
```

### Version-Specific Queries

```
@docs-fetcher: Get the Next.js 13 App Router documentation about
server components and data fetching patterns.
```

## Benefits of Using @docs-fetcher

- **Reduces context bloat** - Only relevant portions are retrieved
- **Ensures current information** - Fetches latest docs, not training data
- **Targeted extraction** - Focuses on specific topics you need
- **Better accuracy** - Uses official sources rather than memory

## Best Practices

1. **Be specific** - Tell docs-fetcher exactly what information you need
2. **Mention the library/framework version** - If version-specific behavior matters
3. **Request examples** - Official examples often show best practices
4. **Use for unfamiliar APIs** - When you're not certain about current syntax
5. **Verify breaking changes** - Check docs when upgrading dependencies

## Example

```
@docs-fetcher: Fetch the PostgreSQL documentation for the JSONB
data type, specifically the containment operators and indexing strategies.
```

## When NOT to Use @docs-fetcher

- For well-known, stable APIs you're confident about
- When you just need a quick syntax reminder for common operations
- For internal project documentation (use code exploration instead)
- When the information is readily available in code comments or type definitions
