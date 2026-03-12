# AI-Agents Build System Refactor Plan

## Goal

Radically simplify the build/install system while maintaining all functionality and making it trivial to add new agent harnesses (like Codex).

## Current State (Problems)

| File | Lines | Issues |
|------|-------|--------|
| `build.sh` | 397 | Fragile YAML parsing with awk/sed, requires yq + jq |
| `install.sh` | 444 | Reinvents rsync, complex overwrite logic |
| `opencode-init.sh` | 102 | Separate script for one config file |
| **Total** | **943** | Hard to maintain, hard to extend |

## Proposed Solution

**Single Python script (~100 lines) with zero external dependencies.**

| Aspect | Old | New |
|--------|-----|-----|
| Scripts | 3 files, 943 lines | 1 file, ~100 lines |
| External deps | `yq`, `jq` | None (Python 3.11+ stdlib) |
| Frontmatter | YAML (`---`) | TOML (`+++`) |
| Adding harness | Modify Bash in multiple places | Add 5-line dict entry |

## Implementation Tasks

### Phase 1: Create the new build system

- [ ] **Task 1.1**: Create `build.py` (~100 lines)
  - TOML frontmatter parsing with `tomllib` (stdlib)
  - Include directive processing (`{{include:filename}}`)
  - Multi-harness output generation
  - Model mapping support (`--work` flag)
  - Install functionality (`--install` flag)

- [ ] **Task 1.2**: Create `migrate_to_toml.py` (one-time use, ~40 lines)
  - Reads all `source/prompts/*.md` files
  - Converts YAML frontmatter (`---`) to TOML frontmatter (`+++`)
  - Preserves markdown content exactly

### Phase 2: Migrate existing prompts

- [ ] **Task 2.1**: Run migration script on all prompt files:
  - `brainstorm.md`
  - `code-full-review.md`
  - `code-performance.md`
  - `code-readability.md`
  - `code-redundancy.md`
  - `code-security.md`
  - `code-simplifier.md`
  - `docs-fetcher.md`
  - `explore.md`
  - `git-commit.md`
  - `sidebar.md`
  - `thorough-plan.md`
  - `_report-only-intro.md` (partial, may not need frontmatter)
  - `_report-only-closing.md` (partial, may not need frontmatter)
  - `AGENTS.md` (base instructions, no frontmatter)

- [ ] **Task 2.2**: Verify migration
  - Run new `build.py`
  - Compare outputs with old `build.sh` outputs
  - Ensure all files generated correctly

### Phase 3: Cleanup

- [ ] **Task 3.1**: Remove old scripts
  - Delete `build.sh`
  - Delete `install.sh`
  - Delete `opencode-init.sh`

- [ ] **Task 3.2**: Update README with new usage

- [ ] **Task 3.3**: Delete `migrate_to_toml.py` (no longer needed)

## TOML Frontmatter Format

### Before (YAML)
```markdown
---
description: Security review specialist...
type: subagent
claude:
  tools: Read, Glob, Grep
  model: claude-opus-4-5
opencode:
  mode: subagent
  model: opencode/gpt-5.4
  reasoningEffort: high
  permission:
    edit: deny
    bash: deny
---
```

### After (TOML)
```markdown
+++
description = "Security review specialist..."
type = "subagent"

[claude]
tools = "Read, Glob, Grep"
model = "claude-opus-4-5"

[opencode]
mode = "subagent"
model = "opencode/gpt-5.4"
reasoningEffort = "high"

[opencode.permission]
edit = "deny"
bash = "deny"
+++
```

## Adding a New Harness (e.g., Codex)

Add entry to `HARNESSES` dict in `build.py`:

```python
HARNESSES = {
    # ... existing ...
    "codex": {
        "agents_dir": "agents",
        "commands_dir": "commands",
        "skills_dir": "skills",
        "base_file": "CODEX.md",
        "install_path": Path.home() / ".codex",
    },
}
```

Then run: `./build.py codex --install`

## Usage After Refactor

```bash
# Build all harnesses
./build.py

# Build specific harness
./build.py opencode

# Build and install
./build.py --install

# Build with work model mappings
./build.py --work --install

# Show help
./build.py --help
```

## Branch Strategy

All work will be done on branch: `refactor/python-build-system`

## Success Criteria

1. All existing prompts converted to TOML format
2. `build.py` produces identical output to old `build.sh`
3. `--install` flag works correctly for both harnesses
4. `--work` flag applies model mappings correctly
5. Zero external dependencies (Python 3.11+ stdlib only)
6. Adding a new harness requires only ~5 lines of code
7. Total codebase reduced from 943 lines to ~100 lines
