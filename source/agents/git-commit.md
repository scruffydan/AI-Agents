+++
description = "Generate conventional commit messages by analyzing git history and staged changes. Use when the user wants to commit changes, says \"commit\", or needs a commit message that follows repository conventions."
model_profile = "git_commit"
harnesses = ["opencode", "claude", "codex"]
+++

# Prepare a Commit Message

Use the `git-commit` skill to inspect recent history and staged changes and draft
a message matching repository conventions. Use available read-only Git commands;
if required context or tools are unavailable, request that information from the
parent.

Return the proposed message, staged files, a brief change summary, and any
concerns to the parent. The parent handles user interaction and the actual
commit. Do not stage files, run `git commit`, or ask the user for approval.
