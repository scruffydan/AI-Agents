---
name: using-docs-fetcher
description: How to use @docs-fetcher to pull current, targeted external documentation (APIs, SDKs, configs, errors, version changes). Use when you need authoritative docs or examples instead of relying on memory.
---

# Request Targeted Documentation

Use the `docs-fetcher` agent when a focused external lookup benefits from a
separate context. Give it the concrete question, installed or targeted version,
known official URLs, and relevant constraints. Request only the details or
examples needed for the task, with source links and compatibility caveats.

For example: "Check the targeted PostgreSQL version's JSONB containment operators
and the indexes supported for this query. Return official sources and a small
applicable example."

Use the environment's actual delegation tools and honor user restrictions. If the
agent or needed web capability is unavailable, fetch the relevant primary
documentation directly when permitted and state any limitation. Prefer local
code and types for internal implementation questions; use `explore` for a
separate codebase investigation when appropriate.

## Example Requests



```
@docs-fetcher: Fetch the Stripe Payment Intents API documentation,
specifically how to create a payment intent with metadata.
```

### Version-Specific Queries

```
@docs-fetcher: Get the Next.js 13 App Router documentation about
server components and data fetching patterns.
```

## When NOT to Use @docs-fetcher

- For well-known, stable APIs you're confident about
- When you just need a quick syntax reminder for common operations
- For internal project documentation (use code exploration instead)
- When the information is readily available in code comments or type definitions
