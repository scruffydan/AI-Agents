#!/usr/bin/env python3
"""Build and install shared configs for selected AI harnesses."""

from __future__ import annotations

import sys

if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11 or newer is required.")

import argparse
from datetime import datetime
import filecmp
from pathlib import Path
import shutil
import tempfile

import build


def select_harnesses() -> list[str]:
    print("Which harnesses would you like to install?")
    print("  1) Codex (default)")
    print("  2) Claude Code")
    print("  3) OpenCode")
    choices = {str(i): name for i, name in enumerate(build.HARNESSES, 1)}
    choices.update({name: name for name in build.HARNESSES})
    while True:
        try:
            selections = input("Enter numbers or names separated by spaces [1]: ").split()
        except EOFError:
            raise ValueError(
                "No selection received. Pass harness names or --all for unattended installs."
            ) from None
        harnesses = []
        for selection in selections or ["codex"]:
            if selection not in choices:
                print(
                    f"Invalid selection: {selection}. Choose 1, 2, 3, codex, claude, or opencode.",
                    file=sys.stderr,
                )
                break
            name = choices[selection]
            if name not in harnesses:
                harnesses.append(name)
        else:
            return harnesses


def same_content(source: Path, destination: Path) -> bool:
    if source.is_file():
        return destination.is_file() and filecmp.cmp(source, destination, shallow=False)
    if not destination.is_dir():
        return False
    entries = {entry.name for entry in source.iterdir() if entry.name != ".DS_Store"}
    return entries == {
        entry.name for entry in destination.iterdir() if entry.name != ".DS_Store"
    } and all(
        same_content(source / name, destination / name) for name in entries
    )


def install(harnesses: list[str], home: Path, force: bool) -> None:
    backup_dir = None

    def install_item(source: Path, destination: Path) -> None:
        nonlocal backup_dir
        if source.name == ".DS_Store":
            return
        if destination.exists() or destination.is_symlink():
            if same_content(source, destination):
                return
            if not force:
                try:
                    answer = input(f"Replace {destination}? [y/N]: ")
                except EOFError:
                    answer = ""
                if answer.strip().lower() not in {"y", "yes"}:
                    print(f"Skipped: {destination}")
                    return
            if backup_dir is None:
                backups = home / ".ai-agents-backups"
                backups.mkdir(parents=True, exist_ok=True)
                backup_dir = Path(tempfile.mkdtemp(
                    prefix=datetime.now().strftime("%Y%m%d-%H%M%S-"), dir=backups,
                ))
            backup = backup_dir / destination.relative_to(home)
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(destination, backup)
            print(f"Backed up: {destination} -> {backup}")

        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, destination, ignore=shutil.ignore_patterns(".DS_Store"))
        else:
            shutil.copy2(source, destination)
        print(f"Installed: {destination}")

    for harness in harnesses:
        output = build.BUILD / harness
        target = home / {
            "codex": ".codex", "claude": ".claude", "opencode": ".config/opencode",
        }[harness]
        layout = build.LAYOUT[harness]
        install_item(output / layout["base"], target / layout["base"])
        agents = output / Path(build.AGENT_PATHS[harness]).parent
        skills = output / layout["skills"]
        skills_target = home / ".agents/skills" if harness == "codex" else target / "skills"
        # Install each entry separately to preserve unrelated agents and skills.
        for source_dir, destination_dir in ((agents, target / "agents"), (skills, skills_target)):
            for entry in sorted(source_dir.glob("*")):
                install_item(entry, destination_dir / entry.name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "harnesses", nargs="*", metavar="{" + ",".join(build.HARNESSES) + "}",
        help="Harnesses to install. Prompts for a selection when omitted (default: codex).",
    )
    parser.add_argument("--all", action="store_true", help="Install all three harnesses.")
    parser.add_argument("--work", action="store_true", help="Use work model mappings.")
    parser.add_argument(
        "--opencode-provider", choices=build.OPENCODE_PROVIDERS,
        help="Override the provider prefix for rendered OpenCode models.",
    )
    parser.add_argument(
        "-y", "--force", action="store_true", help="Replace changed files without prompting.",
    )
    args = parser.parse_intermixed_args(argv)
    unknown = [name for name in args.harnesses if name not in build.HARNESSES]
    if unknown:
        parser.error(f"invalid harness: {', '.join(unknown)} (choose from {', '.join(build.HARNESSES)})")
    if args.all and args.harnesses:
        parser.error("Use --all or explicit harness names, not both.")
    try:
        harnesses = list(build.HARNESSES) if args.all else args.harnesses or select_harnesses()
    except ValueError as exc:
        parser.error(str(exc))
    try:
        build.build(harnesses, work=args.work, opencode_provider=args.opencode_provider)
        install(harnesses, Path.home(), args.force)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Install failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
