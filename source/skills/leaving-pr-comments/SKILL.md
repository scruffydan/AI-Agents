---
name: leaving-pr-comments
description: Format and check comments an agent posts on GitHub for the user, including PR comments, review replies, and reasons for dismissing feedback. Use whenever posting such a comment; not for PR descriptions or commit messages.
---

# Leaving PR Comments

Post a comment only when the user asked for it or the current task already
authorizes it.

Prefix every agent-authored comment left on the user's behalf with this GitHub
note callout:

```md
> [!NOTE]
> 🤖 **<model> responding on behalf of <user>**

Actual comment starts here.
```

Use the verified public name of the model that wrote the comment, and the
user's name or GitHub login.

If the harness does not expose a model name, use the harness name. Do not guess.

Before posting, check the entire comment, including quoted text and
attachments, for secrets and private details.

Keep the attribution inside the note and the actual reply outside it. The
context line must start with the robot emoji. Do not add a horizontal rule,
Setext underline, heading, signature footer, or a second attribution.

Apply this format to top-level PR comments, inline review comments, replies to
bots or reviewers, and written explanations used before resolving or
dismissing feedback. Do not add it to PR descriptions, commit messages, or text
the user explicitly asked to post verbatim without attribution.

Write the comment itself in a direct style:

- Lead with the conclusion.
- Cite the relevant code, behavior, check, or reproduction.
- Keep it concise and avoid filler, canned thanks, or status narration.
- Distinguish verified facts from judgment.

Preview the final Markdown before posting so quoting and blank lines render as
shown. After posting, verify that GitHub returned the comment or review URL.
Resolve a review thread only after its response was posted successfully.

## Source

Adapted from Theo Browne's
[tstack leaving-pr-comments skill](https://github.com/t3dotgg/tstack/blob/6efae364201abc9d9f07443e9caa461f42e51090/skills/leaving-pr-comments/SKILL.md).
The instruction body is unchanged except for the opening authorization
sentence. The description was rewritten to name what the skill covers and
excludes. Upstream's Codex-only `agents/openai.yaml` was not copied, and this
source note was added. The upstream MIT notice is retained in [LICENSE](LICENSE).
