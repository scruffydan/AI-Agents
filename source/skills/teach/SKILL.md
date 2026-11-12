---
name: teach
description: Explain what a concept means or how code works today, from the current code and docs. Use for how-it-works questions, including why code behaves as it does, not why a design was chosen or introduced (use why) or diagnosing failures.
---

# Teach

Start with the user's question and intended understanding. Reuse context already
provided and match their vocabulary and demonstrated knowledge; do not assume a
beginner audience. Ask only when missing material context would change the
explanation. Otherwise answer directly, stating any necessary assumptions.

Teaching or explanation alone stays read-only. Inspect relevant permitted code
and documentation without editing files, running commands that change state, or
creating learning workspaces. An illustrative snippet in the response does not
authorize implementing it. Follow the authorization of any separately requested
implementation work.

## Build the explanation

- Lead with the minimum complete answer to the actual question. Define the key
  concept in plain language and explain what problem it solves, using only the
  prerequisites needed for this question.
- Explain the mechanism incrementally: what starts it, what changes at each step,
  and what result follows. Connect each step to the previous one instead of
  listing terms or jumping between abstraction levels.
- Ground the mechanism in one concrete example. For code, trace a representative
  input through the relevant functions or state changes to its output; point to
  useful source locations. Keep snippets small and distinguish illustrative code
  from code actually inspected.
- Separate observed facts from inferred intent, analogies, and uncertainty. Code
  can establish what happens without establishing why its author chose it.
  Qualify unsupported explanations and identify missing evidence rather than
  inventing a rationale. When the user wants that rationale or its history, use
  the `why` skill instead.
- Use a small diagram only when relationships or flow become easier to understand
  and a suitable format is available. Plain text or a short trace is enough when
  rendering is unavailable; do not require image generation or extra tooling.

## Protect attention

Keep depth proportional to the question. Omit trivia, tangents, repeated
summaries, and long lectures. Use an analogy only when it helps, and explain its
limits when they matter. Include edge cases or trade-offs when they change the
user's understanding or decision, rather than surveying every possibility.

Stop once the question is answered. Let follow-up questions guide further depth;
do not require quizzes, exercises, a curriculum, or a separate learning session.

## Source

Adapted from [pstack teach](https://github.com/cursor/plugins/blob/main/pstack/skills/teach/SKILL.md)
by Lauren Tan in cursor/plugins, under the MIT License. The upstream notice is
retained in [LICENSE](LICENSE). This adaptation keeps the explanation practices
without its mandatory delegation, skill calls, or image generation.
