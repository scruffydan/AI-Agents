# Specification reviewer prompt

Give the reviewer the original task and acceptance criteria, the relevant plan
excerpt, and the exact diff or commits to review. The implementer's report is
context, not proof that the requirements were met.

Use this brief:

> Review the implementation against the supplied requirements. Read the actual
> changes and relevant tests. Identify missing requirements, behavior that
> contradicts the specification, and additions outside the approved scope.
> Distinguish demonstrated failures from questions that need clarification.
>
> Do not modify files. Report each finding with its requirement, file and line,
> observed behavior, and supporting evidence. If there are no findings, say so
> and identify any requirements you could not verify. Perform this review
> yourself; do not delegate it.
