#!/usr/bin/env python3
"""Merge sandbox read_file rules into ~/.gemini/antigravity-cli/settings.json."""

from __future__ import annotations

import sys

if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11 or newer is required.")

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

GIT_PATH_KEYS = ("core.excludesfile", "core.attributesfile")


def external_git_files(home: Path) -> list[Path]:
    """Return resolved global Git config files outside ~/.gitconfig."""
    default = home.resolve() / ".gitconfig"
    env = {**os.environ, "HOME": str(home), "GIT_CONFIG_NOSYSTEM": "1"}
    paths: list[Path] = []

    try:
        listing = subprocess.run(
            ["git", "config", "--includes", "--list", "--show-scope", "--show-origin", "--name-only", "--null"],
            cwd=home, env=env, capture_output=True,
        )
    except FileNotFoundError:
        return []

    if listing.returncode == 0:
        parts = listing.stdout.split(b"\0")
        for i in range(0, len(parts) - 2, 3):
            scope, origin = os.fsdecode(parts[i]), os.fsdecode(parts[i + 1])
            if scope == "global" and origin.startswith("file:"):
                paths.append(Path(origin.removeprefix("file:")).expanduser().resolve())

    for key in GIT_PATH_KEYS:
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
        candidate = xdg_git / name
        if candidate.exists():
            paths.append(candidate.resolve())

    return [p for p in dict.fromkeys(paths) if p != default]


def merge_rules(dest: Path, rules: list[str]) -> tuple[dict, list[str]]:
    data = json.loads(dest.read_text()) if dest.exists() else {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in {dest}")
    perms = {} if data.get("permissions") is None else data["permissions"]
    if not isinstance(perms, dict):
        raise ValueError("'permissions' in settings.json must be a JSON object")
    allow = [] if perms.get("allow") is None else perms["allow"]
    if not isinstance(allow, list) or not all(isinstance(item, str) for item in allow):
        raise ValueError("'permissions.allow' in settings.json must be a list of strings")

    added = [rule for rule in rules if rule not in allow]
    if added:
        data = {**data, "permissions": {**perms, "allow": [*allow, *added]}}
    return data, added


def write_private_json(dest: Path, data: dict) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".settings-", suffix=".tmp", dir=dest.parent)
    tmp_path = Path(tmp)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(data, indent=2) + "\n")
        os.replace(tmp_path, dest)
    except BaseException:
        tmp_path.unlink(missing_ok=True)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Merge read_file rules for external Git config files into ~/.gemini/antigravity-cli/settings.json.",
    )
    parser.add_argument("-y", "--yes", action="store_true", help="Update existing settings without prompting (backs up first).")
    parser.add_argument("--allow-read", action="append", default=[], metavar="PATH", help="Extra read-only path to allow (repeatable).")
    args = parser.parse_args(argv)

    home = Path.home()
    dest = home / ".gemini" / "antigravity-cli" / "settings.json"
    if dest.is_symlink():
        sys.exit(f"Error: refusing to overwrite symlink target {dest}")
    if dest.exists() and not dest.is_file():
        sys.exit(f"Error: {dest} is not a regular file")

    paths = list(dict.fromkeys([
        *external_git_files(home),
        *(Path(raw).expanduser().resolve() for raw in args.allow_read),
    ]))
    rules = []
    for path in paths:
        text = path.as_posix()
        if any(ch in text for ch in ("\n", "\r", ")")):
            sys.exit(f"Error: unsupported characters in path: {text}")
        rules.append(f"read_file({text})")

    if not rules:
        print("No external Git config files detected; nothing to add.")
        return 0

    try:
        merged, added = merge_rules(dest, rules)
    except (ValueError, OSError) as exc:
        sys.exit(f"Error: {exc}")

    if dest.is_file() and not added:
        os.chmod(dest, 0o600)
        print(f"Unchanged: {dest}")
        return 0

    if dest.is_file() and not args.yes:
        print(f"Rules to add to {dest}:\n" + "\n".join(f"  {rule}" for rule in added))
        try:
            answer = input(f"Update {dest} (backup first)? [y/N]: ")
        except EOFError:
            sys.exit("Aborted: no confirmation received.")
        if answer.strip().lower() not in {"y", "yes"}:
            print("Aborted.")
            return 0

    existed = dest.is_file()
    if existed:
        backups = home / ".ai-agents-backups"
        backups.mkdir(parents=True, exist_ok=True)
        backup_dir = Path(tempfile.mkdtemp(prefix=f"antigravity-{datetime.now():%Y%m%d-%H%M%S}-", dir=backups))
        os.chmod(backup_dir, 0o700)
        backup = backup_dir / dest.name
        shutil.copyfile(dest, backup)
        os.chmod(backup, 0o600)
        print(f"Backed up: {dest} -> {backup}")

    write_private_json(dest, merged)
    print(f"{'Updated' if existed else 'Installed'}: {dest}")
    for rule in added:
        print(f"  + {rule}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
