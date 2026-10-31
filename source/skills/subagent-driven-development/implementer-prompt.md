# Implementer prompt

Provide the child agent with the full task, relevant plan excerpt, acceptance
criteria, allowed files, repository context, and verification commands. Include
any dependencies on other tasks and whether a commit is authorized.

Use this brief:

> Implement the supplied task within its stated scope. Inspect the relevant
> code and instructions first, and preserve unrelated changes in the shared
> workspace. Resolve routine implementation choices from the repository's
> conventions. Ask the parent when missing information materially changes the
> behavior or prevents progress.
>
> Run the checks needed to verify the acceptance criteria and inspect your diff.
> Report what changed, the files affected, verification results, and remaining
> concerns. Commit only when the brief authorizes it. Perform this task yourself;
> delegate further only if the brief explicitly permits it.
