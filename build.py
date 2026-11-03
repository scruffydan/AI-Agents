#!/usr/bin/env python3
"""Build native harness configs from shared agents, prompts, and skills."""

from __future__ import annotations

import sys

if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11 or newer is required.")

import argparse
import re
import shutil
import tomllib
from functools import lru_cache
from pathlib import Path

import renderers

ROOT = Path(__file__).resolve().parent
PROMPTS = ROOT / "source" / "prompts"
AGENTS = ROOT / "source" / "agents"
SKILLS = ROOT / "source" / "skills"
MODELS_FILE = ROOT / "source" / "models.toml"
BUILD = ROOT / "build"

HARNESSES = ("codex", "claude", "opencode")
OPENCODE_PROVIDERS = ("openai", "opencode")
INCLUDE_RE = re.compile(r"\{\{include:([A-Za-z0-9_.-]+)\}\}")
NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
LAYOUT = {
    "opencode": {"base": "AGENTS.md", "skills": "skills"},
    "claude": {"base": "CLAUDE.md", "skills": "skills"},
    "codex": {"base": "AGENTS.md", "skills": ".agents/skills"},
}
AGENT_PATHS = {
    "claude": "agents/{name}.md",
    "opencode": "agents/{name}.md",
    "codex": ".codex/agents/{name}.toml",
}


def validate_name(name: str) -> str:
    if not NAME_RE.fullmatch(name) or len(name) > 64:
        raise ValueError("Names must use lowercase letters/digits and single hyphens (max 64 characters).")
    return name


def validate_harnesses(harnesses: list[str]) -> list[str]:
    if not isinstance(harnesses, list) or not harnesses:
        raise ValueError("harnesses must be a non-empty list")
    if any(not isinstance(h, str) or h not in HARNESSES for h in harnesses):
        raise ValueError(f"harnesses must be selected from {', '.join(HARNESSES)}")
    if len(set(harnesses)) != len(harnesses):
        raise ValueError("Duplicate harness selection")
    return harnesses


@lru_cache
def model_profiles() -> dict[str, dict[str, str]]:
    with MODELS_FILE.open("rb") as handle:
        return tomllib.load(handle)


def resolve_model(
    profile: str,
    harness: str,
    work: bool,
    opencode_provider: str | None,
) -> str:
    try:
        values = model_profiles()[profile]
    except KeyError as exc:
        raise ValueError(f"Unknown model profile: {profile}") from exc

    work_key = f"{harness}_work"
    key = work_key if work and work_key in values else harness
    try:
        model = values[key]
    except KeyError as exc:
        raise ValueError(f"Profile {profile!r} has no model for {harness}") from exc

    if not isinstance(model, str) or not model.strip():
        raise ValueError(f"Profile {profile!r} must provide a non-empty model for {harness}")

    if harness == "opencode" and opencode_provider:
        _, separator, name = model.partition("/")
        if not separator:
            raise ValueError(f"OpenCode model must include a provider: {model}")
        model = f"{opencode_provider}/{name}"
    return model


def load_agents() -> dict[str, dict]:
    agents = {}
    for path in sorted(AGENTS.glob("*.md")):
        name = validate_name(path.stem)
        lines = path.read_text().splitlines(keepends=True)
        if not lines or lines[0].strip() != "+++":
            raise ValueError(f"{path}: expected +++ TOML frontmatter")
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "+++"), None)
        if end is None:
            raise ValueError(f"{path}: missing closing +++")
        metadata = tomllib.loads("".join(lines[1:end]))
        unknown = metadata.keys() - {"description", "model_profile", "harnesses"}
        if unknown:
            raise ValueError(f"{path}: unknown fields: {', '.join(sorted(unknown))}")
        for field in ("description", "model_profile"):
            if not isinstance(metadata.get(field), str) or not metadata[field].strip():
                raise ValueError(f"{path}: {field} must be a non-empty string")
        if "\n" in metadata["description"] or "\r" in metadata["description"]:
            raise ValueError(f"{path}: description must be a single line")
        targets = validate_harnesses(metadata.get("harnesses", list(HARNESSES)))
        for harness in targets:
            resolve_model(metadata["model_profile"], harness, False, None)
        body = expand_includes("".join(lines[end + 1:]), ()).strip()
        if not body:
            raise ValueError(f"{path}: agent body must not be empty")
        agents[name] = dict(metadata, name=name, harnesses=targets, body=body)
    return agents


def expand_includes(text: str, stack: tuple[str, ...]) -> str:
    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in stack:
            chain = " -> ".join((*stack, name))
            raise ValueError(f"Recursive prompt include: {chain}")
        path = PROMPTS / name
        if not path.is_file():
            raise ValueError(f"Missing prompt include: {name}")
        return expand_includes(path.read_text(), (*stack, name)).strip()

    return INCLUDE_RE.sub(replace, text)


def build(
    harnesses: list[str],
    work: bool = False,
    opencode_provider: str | None = None,
) -> int:
    validate_harnesses(harnesses)
    if work and opencode_provider:
        raise ValueError("--work cannot be combined with --opencode-provider; work models use Google Vertex.")
    model_profiles.cache_clear()
    agents = load_agents()

    # Finish rendering before replacing the previous successful build.
    outputs = {}

    def add(harness: str, name: str, rendered: str) -> None:
        destination = Path(harness) / AGENT_PATHS[harness].format(name=name)
        if destination in outputs:
            raise ValueError(f"Duplicate output: {destination}")
        outputs[destination] = rendered

    for harness in harnesses:
        for name, agent in agents.items():
            if harness in agent["harnesses"]:
                model = resolve_model(agent["model_profile"], harness, work, opencode_provider)
                add(harness, name, renderers.RENDERERS[harness](agent, model))
        if harness == "opencode":
            plan = renderers.OPENCODE_PLAN
            add(harness, plan["name"], renderers.render_opencode(plan, None))

    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir()

    for harness in harnesses:
        output_dir = BUILD / harness
        output_dir.mkdir(parents=True)
        layout = LAYOUT[harness]
        shutil.copy(PROMPTS / "AGENTS.md", output_dir / layout["base"])
        shutil.copytree(
            SKILLS, output_dir / layout["skills"], ignore=shutil.ignore_patterns(".DS_Store"),
        )

    for relative, rendered in outputs.items():
        destination = BUILD / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered)

    artifact_count = len(outputs)
    environment = "work" if work else "default"
    print(f"Built {artifact_count} prompt configs for {', '.join(harnesses)} ({environment})")
    print(f"Output: {BUILD}")
    return artifact_count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build native AI harness configs from shared source files."
    )
    parser.add_argument(
        "harnesses",
        nargs="*",
        metavar="{" + ",".join(HARNESSES) + "}",
        help="Harnesses to build. Defaults to all.",
    )
    parser.add_argument("--work", action="store_true", help="Use work model mappings.")
    parser.add_argument(
        "--opencode-provider",
        choices=OPENCODE_PROVIDERS,
        help="Override the provider prefix for rendered OpenCode models.",
    )
    args = parser.parse_args(argv)
    # Python < 3.12 rejects an empty nargs="*" list when choices is set.
    unknown = [name for name in args.harnesses if name not in HARNESSES]
    if unknown:
        parser.error(f"invalid harness: {', '.join(unknown)} (choose from {', '.join(HARNESSES)})")
    try:
        build(
            args.harnesses or list(HARNESSES),
            work=args.work,
            opencode_provider=args.opencode_provider,
        )
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Build failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
