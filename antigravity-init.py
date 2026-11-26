#!/usr/bin/env python3
"""Add read_file rules for external Git configs to ~/.gemini/antigravity-cli/settings.json."""

import json
import os
from pathlib import Path
import shutil
import subprocess


def external_git_files(home: Path) -> list[Path]:
    default = home.resolve() / ".gitconfig"
    env = {**os.environ, "HOME": str(home), "GIT_CONFIG_NOSYSTEM": "1"}
    paths: list[Path] = []

    res = subprocess.run(
        ["git", "config", "--includes", "--list", "--show-scope", "--show-origin", "--name-only", "--null"],
        cwd=home, env=env, capture_output=True,
    )
    if res.returncode == 0:
        parts = res.stdout.split(b"\0")
        for i in range(0, len(parts) - 2, 3):
            scope, origin = os.fsdecode(parts[i]), os.fsdecode(parts[i + 1])
            if scope == "global" and origin.startswith("file:"):
                paths.append(Path(origin.removeprefix("file:")).expanduser().resolve())

    for key in ("core.excludesfile", "core.attributesfile"):
        res = subprocess.run(
            ["git", "config", "--includes", "--show-scope", "--path", "--get-all", "--null", key],
            cwd=home, env=env, capture_output=True,
        )
        if res.returncode == 0:
            parts = res.stdout.split(b"\0")
            for i in range(0, len(parts) - 1, 2):
                scope, raw = os.fsdecode(parts[i]), os.fsdecode(parts[i + 1]).strip()
                if scope == "global" and raw:
                    paths.append(Path(raw).expanduser().resolve())

    xdg_raw = os.environ.get("XDG_CONFIG_HOME", "")
    xdg_git = (Path(xdg_raw) if xdg_raw.startswith("/") else home / ".config") / "git"
    for name in ("ignore", "attributes"):
        if (xdg_git / name).exists():
            paths.append((xdg_git / name).resolve())

    return [p for p in dict.fromkeys(paths) if p != default]


def main() -> int:
    home = Path.home()
    rules = [f"read_file({p.as_posix()})" for p in external_git_files(home)]
    if not rules:
        print("No external Git config files detected; nothing to add.")
        return 0

    dest = home / ".gemini/antigravity-cli/settings.json"
    data = json.loads(dest.read_text()) if dest.exists() else {}
    allow = data.setdefault("permissions", {}).setdefault("allow", [])
    added = [r for r in rules if r not in allow]
    if not added:
        print(f"Unchanged: {dest}")
        return 0

    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        bak = dest.with_suffix(".json.bak")
        shutil.copyfile(dest, bak)
        os.chmod(bak, 0o600)
    allow.extend(added)
    dest.write_text(json.dumps(data, indent=2) + "\n")
    os.chmod(dest, 0o600)
    print(f"Updated: {dest}")
    for rule in added:
        print(f"  + {rule}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
