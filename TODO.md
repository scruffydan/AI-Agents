# TODO

## Before merging

- [ ] Ensure the normal `python3` on the target machine is Python 3.11 or newer,
      or set `PYTHON` when running `install.sh`.
- [ ] Install OpenCode by itself and confirm its agents, commands, and skills are
      discovered.
- [ ] Install Claude Code by itself and confirm its agents and skills are
      discovered.
- [ ] Install Codex by itself and confirm its agents and skills are discovered.
- [ ] Verify one `--work` build and one OpenCode provider override against the
      providers actually used day to day.
- [ ] Review the provider-native templates and remove prompts or skills that are
      no longer useful.
- [ ] Try `new.py agent` and `new.py skill` for the next addition; edit their TODO
      instructions before installing and add an override only when needed.

## Later, only if needed

- [ ] Decide whether installation should use repository symlinks instead of
      replacing managed directories.
- [ ] Extend the small authoring tests only when a real bug or harness-format
      change needs coverage.

## Explicit non-goals

- No plugin or harness registry.
- No manifest, doctor command, schema versioning, or install planner.
- No general-purpose rendering framework.
