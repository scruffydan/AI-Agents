#!/usr/bin/env python3
"""Create one shared agent definition or skill folder without overwriting files."""

from __future__ import annotations

import argparse
import json
import sys

if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11 or newer is required.")

import build


def create_agent(name: str, description: str, profile: str, harnesses: list[str]) -> None:
    build.validate_name(name)
    build.validate_harnesses(harnesses)
    for harness in harnesses:
        build.resolve_model(profile, harness, False, None)
        _, pattern = build.AGENT_PATHS[harness]
        if (build.TEMPLATES / harness / pattern.format(name=name)).exists():
            raise ValueError(f"{harness} already has an explicit agent template named {name}")
    path = build.AGENTS / f"{name}.md"
    content = (
        f"+++\ndescription = {json.dumps(description, ensure_ascii=False)}\n"
        f"model_profile = {json.dumps(profile)}\n"
        f"harnesses = {json.dumps(harnesses)}\n+++\n\n"
        f"# {name.replace('-', ' ').title()}\n\n"
        "TODO: Describe the task, workflow, boundaries, and expected output.\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as handle:
        handle.write(content)
    print(f"Created: {path}")


def create_skill(name: str, description: str) -> None:
    build.validate_name(name)
    for harness in build.HARNESSES:
        template = build.TEMPLATES / harness / build.LAYOUT[harness]["skills"] / name
        if template.exists():
            raise ValueError(f"{harness} already has a templated skill named {name}")
    path = build.SKILLS / name
    path.mkdir()  # Exclusive: never replace an existing folder or symlink.
    (path / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {json.dumps(description, ensure_ascii=False)}\n---\n\n"
        f"# {name.replace('-', ' ').title()}\n\n"
        "TODO: Describe when to use this skill, its steps, and the expected result.\n"
    )
    print(f"Created: {path / 'SKILL.md'}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="kind", required=True)
    agent = commands.add_parser("agent", help="Create a shared subagent definition")
    skill = commands.add_parser("skill", help="Create a shared skill folder")
    for command in (agent, skill):
        command.add_argument("name", help="Lowercase words separated by hyphens")
        command.add_argument("--description", default="TODO: Describe the purpose and when to use this.")
    agent.add_argument("--profile", default="deep_review", help="Model profile in source/models.toml")
    agent.add_argument("--harness", action="append", choices=build.HARNESSES, help="Repeat to select targets; defaults to all")
    args = parser.parse_args(argv)
    try:
        if not args.description.strip() or "\n" in args.description or "\r" in args.description:
            raise ValueError("Description must be a non-empty single line")
        if args.kind == "agent":
            create_agent(args.name, args.description, args.profile, args.harness or list(build.HARNESSES))
        else:
            create_skill(args.name, args.description)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Creation failed: {exc}\n")
    print("Edit the new file, then run ./build.py. Nothing has been installed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
