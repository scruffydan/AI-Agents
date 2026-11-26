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


def _resolved(path: Path) -> Path:
    return path.expanduser().resolve()


def _dedupe(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in paths:
        if path not in seen:
            seen.add(path)
            unique.append(path)
    return unique


def detect_external_git_files(home: Path) -> list[Path]:
    """Return resolved global Git config files outside ~/.gitconfig."""
    default_gitconfig = home.resolve() / ".gitconfig"
    env = {**os.environ, "HOME": str(home)}
    paths: list[Path] = []

    try:
        listing = subprocess.run(
            ["git", "config", "--global", "--includes", "--list", "--show-origin", "--name-only", "--null"],
            env=env, capture_output=True,
        )
    except FileNotFoundError:
        return []

    if listing.returncode == 0:
        parts = listing.stdout.split(b"\0")
        for index in range(0, len(parts) - 1, 2):
            origin = os.fsdecode(parts[index])
            if not origin.startswith("file:"):
                continue
            target = _resolved(Path(origin.removeprefix("file:")))
            if target != default_gitconfig:
                paths.append(target)

    for key in GIT_PATH_KEYS:
        result = subprocess.run(
            ["git", "config", "--global", "--includes", "--path", "--get", key],
            env=env, capture_output=True, text=True,
        )
        if result.returncode == 0:
            raw = result.stdout.strip()
            if raw:
                target = _resolved(Path(raw))
                if target != default_gitconfig:
                    paths.append(target)

    return _dedupe(paths)


def format_rule(path: Path) -> str:
    text = path.as_posix()
    if any(ch in text for ch in ("\n", "\r", ")")):
        raise ValueError(f"Unsupported characters in read_file path: {text}")
    return f"read_file({text})"


def load_settings(dest: Path) -> dict:
    if not dest.exists():
        return {}
    try:
        data = json.loads(dest.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {dest}: {exc}") from None
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in {dest}")
    return data


def merge_allow_rules(data: dict, rules: list[str]) -> tuple[dict, list[str]]:
    merged = dict(data)
    permissions = merged.get("permissions")
    if permissions is None:
        permissions = {}
    elif not isinstance(permissions, dict):
        raise ValueError("'permissions' in settings.json must be a JSON object")
    else:
        permissions = dict(permissions)

    allow = permissions.get("allow")
    if allow is None:
        allow = []
    elif not isinstance(allow, list) or not all(isinstance(item, str) for item in allow):
        raise ValueError("'permissions.allow' in settings.json must be a list of strings")
    else:
        allow = list(allow)

    added = [rule for rule in rules if rule not in allow]
    if added:
        allow.extend(added)
        permissions["allow"] = allow
        merged["permissions"] = permissions
    return merged, added


def write_private_json(dest: Path, data: dict) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(data, indent=2) + "\n"
    fd, tmp_name = tempfile.mkstemp(prefix=".settings-", suffix=".tmp", dir=dest.parent)
    tmp_path = Path(tmp_name)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(body)
        os.replace(tmp_path, dest)
    except BaseException:
        tmp_path.unlink(missing_ok=True)
        raise


def back_up(dest: Path, home: Path) -> Path:
    backups = home / ".ai-agents-backups"
    backups.mkdir(parents=True, exist_ok=True)
    backup_dir = Path(tempfile.mkdtemp(
        prefix=f"antigravity-{datetime.now().strftime('%Y%m%d-%H%M%S')}-", dir=backups,
    ))
    os.chmod(backup_dir, 0o700)
    backup = backup_dir / dest.name
    shutil.copyfile(dest, backup)
    os.chmod(backup, 0o600)
    return backup


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Merge read_file sandbox allow rules for external Git config files into "
            "~/.gemini/antigravity-cli/settings.json without replacing other settings."
        ),
    )
    parser.add_argument(
        "-y", "--yes", action="store_true",
        help="Update an existing settings.json without prompting (backs up first).",
    )
    parser.add_argument(
        "--allow-read", action="append", default=[], metavar="PATH",
        help="Additional file or directory path to allow read-only inside the sandbox (repeatable).",
    )
    args = parser.parse_args(argv)

    home = Path.home()
    dest = home / ".gemini" / "antigravity-cli" / "settings.json"

    if dest.is_symlink():
        print(f"Error: refusing to overwrite symlink target {dest}", file=sys.stderr)
        return 1
    if dest.exists() and not dest.is_file():
        print(f"Error: {dest} is not a regular file", file=sys.stderr)
        return 1

    try:
        paths = _dedupe([
            *detect_external_git_files(home),
            *(_resolved(Path(raw)) for raw in args.allow_read),
        ])
        rules = [format_rule(path) for path in paths]
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not rules:
        print("No external Git config files detected; nothing to add.")
        return 0

    try:
        existing = load_settings(dest)
        merged, added = merge_allow_rules(existing, rules)
    except (ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if dest.is_file() and not added:
        os.chmod(dest, 0o600)
        print(f"Unchanged: {dest}")
        return 0

    if dest.is_file() and not args.yes:
        print(f"Rules to add to {dest}:")
        for rule in added:
            print(f"  {rule}")
        try:
            answer = input(f"Update {dest} (backup first)? [y/N]: ")
        except EOFError:
            print("Aborted: no confirmation received.")
            return 1
        if answer.strip().lower() not in {"y", "yes"}:
            print("Aborted.")
            return 0

    existed = dest.is_file()
    if existed:
        backup = back_up(dest, home)
        print(f"Backed up: {dest} -> {backup}")

    write_private_json(dest, merged)
    action = "Updated" if existed else "Installed"
    print(f"{action}: {dest}")
    for rule in added:
        print(f"  + {rule}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
