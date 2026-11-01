---
name: using-docs-fetcher
description: Delegate external documentation research to the docs-fetcher subagent. Use when API, framework, configuration, or version-specific facts need checking while keeping documentation pages out of the main conversation.
---

# Request Targeted Documentation

Use the environment's delegation tools to launch the `docs-fetcher` subagent for
external documentation lookups. Keep searching, fetching, and extracting pages
in that child's context. The parent should receive focused findings, not full
documentation pages.

Give the child the concrete question, installed or targeted version, known
official URLs, and relevant constraints. Request a compact answer with the needed
details or examples, source links, version caveats, and unresolved uncertainty.
The child performs the lookup itself without delegating further.

For example: "Check the targeted PostgreSQL version's JSONB containment operators
and the indexes supported for this query. Return official sources and a small
applicable example."

Use the returned findings to continue the task. Send follow-up documentation
questions to the child rather than fetching the pages again in the parent.

Honor the user's delegation restrictions. If the agent or needed web capability
is unavailable, explain the limitation and continue independent authorized work.
Do not search or fetch documentation in the main conversation as a fallback.
Local code, types, and repository documentation can still be inspected directly;
this isolation rule applies to external documentation lookups.

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
