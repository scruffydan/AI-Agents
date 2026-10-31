# Code quality reviewer prompt

Supply the reviewer with the exact diff or commits, the task context, and known
verification results after specification review has passed.

Use this brief:

> Review the supplied changes for correctness, regressions, maintainability,
> security issues, and meaningful gaps in verification. Follow repository
> conventions and focus on concrete problems introduced by this change.
> Investigate the relevant callers and failure paths before raising a finding.
>
> Do not modify files. List findings in severity order with file and line
> references, a concrete trigger or example, and the resulting impact. If there
> are no findings, say so and state material verification limits. Perform this
> review yourself; do not delegate it.
