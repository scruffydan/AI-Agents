#!/usr/bin/env python3
"""Render provider-native templates into build/.

Templates define the exact output format. This script only expands prompt bodies,
model profiles, and shared prompt includes.
"""

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

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / "templates"
PROMPTS = ROOT / "source" / "prompts"
SKILLS = ROOT / "source" / "skills"
MODELS_FILE = ROOT / "source" / "models.toml"
BUILD = ROOT / "build"

HARNESSES = ("opencode", "claude", "codex")
OPENCODE_PROVIDERS = ("openai", "github-copilot", "opencode")
TOKEN_RE = re.compile(r"\{\{(prompt|model):([a-z0-9_-]+)\}\}")
INCLUDE_RE = re.compile(r"\{\{include:([A-Za-z0-9_.-]+)\}\}")
LAYOUT = {
    "opencode": {"base": "AGENTS.md", "skills": "skill"},
    "claude": {"base": "CLAUDE.md", "skills": "skills"},
    "codex": {"base": "AGENTS.md", "skills": ".agents/skills"},
}


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

    if harness == "opencode" and opencode_provider:
        _, separator, name = model.partition("/")
        if not separator:
            raise ValueError(f"OpenCode model must include a provider: {model}")
        model = f"{opencode_provider}/{name}"
    return model


@lru_cache
def prompt_body(name: str) -> str:
    path = PROMPTS / f"{name}.md"
    if not path.is_file():
        raise ValueError(f"Unknown prompt: {name}")
    return expand_includes(path.read_text(), (path.name,)).strip()


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


def render_template(
    path: Path,
    harness: str,
    work: bool,
    opencode_provider: str | None,
) -> str:
    def replace(match: re.Match[str]) -> str:
        kind, name = match.groups()
        if kind == "prompt":
            return prompt_body(name)
        return resolve_model(name, harness, work, opencode_provider)

    rendered = TOKEN_RE.sub(replace, path.read_text())
    if TOKEN_RE.search(rendered) or INCLUDE_RE.search(rendered):
        raise ValueError(f"Unresolved template token in {path}")
    if path.suffix == ".toml":
        tomllib.loads(rendered)
    return rendered


def build(
    harnesses: list[str],
    work: bool = False,
    opencode_provider: str | None = None,
) -> int:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir()

    artifact_count = 0
    for harness in harnesses:
        source_dir = TEMPLATES / harness
        output_dir = BUILD / harness
        output_dir.mkdir(parents=True)
        layout = LAYOUT[harness]
        shutil.copy(PROMPTS / "AGENTS.md", output_dir / layout["base"])
        shutil.copytree(SKILLS, output_dir / layout["skills"])

        for template in sorted(path for path in source_dir.rglob("*") if path.is_file()):
            destination = output_dir / template.relative_to(source_dir)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(
                render_template(template, harness, work, opencode_provider)
            )
            artifact_count += 1

    environment = "work" if work else "default"
    print(f"Built {artifact_count} prompt configs for {', '.join(harnesses)} ({environment})")
    print(f"Output: {BUILD}")
    return artifact_count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render AI harness configs from provider-native templates."
    )
    parser.add_argument(
        "harnesses",
        nargs="*",
        choices=HARNESSES,
        help="Harnesses to build. Defaults to all.",
    )
    parser.add_argument("--work", action="store_true", help="Use work model mappings.")
    parser.add_argument(
        "--opencode-provider",
        choices=OPENCODE_PROVIDERS,
        help="Override the provider prefix for rendered OpenCode models.",
    )
    args = parser.parse_args(argv)
    build(
        args.harnesses or list(HARNESSES),
        work=args.work,
        opencode_provider=args.opencode_provider,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
