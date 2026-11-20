#!/usr/bin/env python3
"""Build and install shared configs for selected AI harnesses."""

from __future__ import annotations

import sys

if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11 or newer is required.")

import argparse
from datetime import datetime
import filecmp
import os
import re
from pathlib import Path
import shutil
import subprocess
import tempfile
from urllib.parse import urlsplit

import build

# Agents this repository used to install and no longer builds. Installing moves
# leftover copies to the backup folder. A name the build still produces is
# skipped, so a name can be listed before its removal lands and reused later.
RETIRED_AGENTS = ("code-readability", "code-redundancy", "code-simplifier")


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
    entries = {entry.name for entry in source.iterdir() if not build.is_os_metadata(entry.name)}
    return entries == {
        entry.name for entry in destination.iterdir() if not build.is_os_metadata(entry.name)
    } and all(
        same_content(source / name, destination / name) for name in entries
    )


def install(harnesses: list[str], home: Path, force: bool) -> None:
    backup_dir = None

    def back_up(destination: Path, action: str) -> bool:
        nonlocal backup_dir
        if not force:
            try:
                answer = input(f"{action} {destination}? [y/N]: ")
            except EOFError:
                answer = ""
            if answer.strip().lower() not in {"y", "yes"}:
                print(f"Skipped: {destination}")
                return False
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
        return True

    def install_item(source: Path, destination: Path) -> None:
        if build.is_os_metadata(source.name):
            return
        if destination.exists() or destination.is_symlink():
            if same_content(source, destination):
                return
            if not back_up(destination, "Replace"):
                return

        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, destination, ignore=build.ignore_os_metadata)
        else:
            shutil.copy2(source, destination)
        print(f"Installed: {destination}")

    for harness in harnesses:
        output = build.BUILD / harness
        target = home / {
            "codex": ".codex", "claude": ".claude", "opencode": ".config/opencode",
        }[harness]
        layout = build.LAYOUT[harness]
        install_item(output / "THIRD_PARTY_NOTICES.md", target / "THIRD_PARTY_NOTICES.md")
        install_item(output / layout["base"], target / layout["base"])
        agents = output / Path(build.AGENT_PATHS[harness]).parent
        skills = output / layout["skills"]
        skills_target = home / ".agents/skills" if harness == "codex" else target / "skills"
        # Install each entry separately to preserve unrelated agents and skills.
        for source_dir, destination_dir in ((agents, target / "agents"), (skills, skills_target)):
            for entry in sorted(source_dir.glob("*")):
                install_item(entry, destination_dir / entry.name)
        suffix = Path(build.AGENT_PATHS[harness]).suffix
        for name in RETIRED_AGENTS:
            leftover = target / "agents" / f"{name}{suffix}"
            if (agents / leftover.name).exists():
                continue
            if (leftover.exists() or leftover.is_symlink()) and back_up(leftover, "Retire"):
                print(f"Retired: {leftover}")


def repository_destination(source: str, home: Path) -> Path:
    if source.startswith("-") or "::" in source:
        raise ValueError("Use a Git URL, SSH repository address, or local repository path.")
    if "://" in source:
        path = urlsplit(source).path
    elif re.match(r"[^/]+:", source):
        path = source.split(":", 1)[1]
    else:
        path = str(Path(source).resolve())
    name = path.rstrip("/").rsplit("/", 1)[-1]
    name = name.removesuffix(".git")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name) or name == "local.md":
        raise ValueError("Repository name must be a directory name distinct from local.md.")
    return home / "Knowledge" / name


def clone_repository(source: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Reserve an empty destination without following or replacing an existing path.
    destination.mkdir(mode=0o700)
    result = subprocess.run(["git", "clone", "--", source, str(destination)])
    if result.returncode:
        raise ValueError(f"Git clone failed; inspect {destination} before retrying.")


def init_local_context(home: Path, repository: Path | None = None) -> None:
    destination = home / ".config/ai-agents/local.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    text = (
        "# Machine-local context\n\n"
        "Add machine-specific context and approved knowledge sources here.\n\n"
        "For a wiki, replace `<repo-name>` in `~/Knowledge/<repo-name>/AGENTS.md`\n"
        "with its checkout directory name, and describe its access boundaries.\n"
        "Omit the knowledge pointer on machines without a knowledge store.\n\n"
        "Keep private paths and content out of the shared AI-Agents repository.\n"
    )
    if repository is not None:
        startup = f"~/Knowledge/{repository.name}/AGENTS.md"
        text = (
            "# Machine-local context\n\n"
            f"For shared knowledge, read `{startup}`.\n\n"
            "If the checkout or AGENTS.md is unavailable, report that and continue without it.\n"
            "Follow its selective retrieval and correction guidance when available.\n"
            "Keep capture and curation in the knowledge project.\n"
            "This grants no additional access or publishing permissions.\n\n"
            "When a change lands on a project's default branch, check whether it makes an\n"
            "existing wiki summary materially out of date. If it does, follow the wiki's\n"
            "authorized inbox workflow and link to the landed revision.\n"
        )
    try:
        fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        print(f"Preserved existing local context: {destination}")
        return
    with os.fdopen(fd, "w") as handle:
        handle.write(text)
    print(f"Created local context: {destination}")


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "harnesses", nargs="*", metavar="{" + ",".join(build.HARNESSES) + "}",
        help="Harnesses to install. Prompts for a selection when omitted (default: codex).",
    )
    parser.add_argument("--all", action="store_true", help="Install all three harnesses.")
    parser.add_argument("--work", action="store_true", help="Use work model mappings.")
    parser.add_argument(
        "--init-local", action="store_true",
        help="Create ~/.config/ai-agents/local.md if absent; never replace existing local context.",
    )
    parser.add_argument(
        "--opencode-provider", choices=build.OPENCODE_PROVIDERS,
        help="Override the provider prefix for rendered OpenCode models.",
    )
    parser.add_argument(
        "-y", "--force", action="store_true", help="Replace changed files without prompting.",
    )
    parser.add_argument(
        "--clone-repo", metavar="URL",
        help="Clone a repository into ~/Knowledge/<repo-name>; destination must not exist.",
    )
    args = parser.parse_intermixed_args(arguments)
    unknown = [name for name in args.harnesses if name not in build.HARNESSES]
    if unknown:
        parser.error(f"invalid harness: {', '.join(unknown)} (choose from {', '.join(build.HARNESSES)})")
    if args.all and args.harnesses:
        parser.error("Use --all or explicit harness names, not both.")
    try:
        harnesses = list(build.HARNESSES) if args.all else args.harnesses or select_harnesses()
        if not arguments:
            try:
                answer = input("Create machine-local context (local.md)? [y/N]: ")
                args.init_local = answer.strip().lower() in {"y", "yes"}
                args.clone_repo = input("Repository URL or path to clone [Enter to skip]: ").strip() or None
            except EOFError:
                # Leave unanswered optional setup at its default.
                pass
    except ValueError as exc:
        parser.error(str(exc))
    try:
        build.build(harnesses, work=args.work, opencode_provider=args.opencode_provider)
        repository = None
        try:
            if args.clone_repo:
                repository = repository_destination(args.clone_repo, Path.home())
                clone_repository(args.clone_repo, repository)
        finally:
            if args.init_local:
                init_local_context(Path.home(), repository)
        install(harnesses, Path.home(), args.force)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Install failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
