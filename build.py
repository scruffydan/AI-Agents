#!/usr/bin/env python3
"""Render provider-native templates into build/.

Templates define the native output format. Agents share definitions and default
templates; commands and modes use explicit templates.
"""

from __future__ import annotations

import sys

if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11 or newer is required.")

import argparse
import json
import re
import shutil
import tomllib
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / "templates"
PROMPTS = ROOT / "source" / "prompts"
AGENTS = ROOT / "source" / "agents"
SKILLS = ROOT / "source" / "skills"
MODELS_FILE = ROOT / "source" / "models.toml"
BUILD = ROOT / "build"

HARNESSES = ("opencode", "claude", "codex")
OPENCODE_PROVIDERS = ("openai", "github-copilot", "opencode")
TOKEN_RE = re.compile(r"\{\{(prompt|model|agent):([a-z0-9_-]+)\}\}")
INCLUDE_RE = re.compile(r"\{\{include:([A-Za-z0-9_.-]+)\}\}")
NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
LAYOUT = {
    "opencode": {"base": "AGENTS.md", "skills": "skill"},
    "claude": {"base": "CLAUDE.md", "skills": "skills"},
    "codex": {"base": "AGENTS.md", "skills": ".agents/skills"},
}
AGENT_PATHS = {
    "claude": ("agent.md", "agents/{name}.md"),
    "opencode": ("agent.md", "agent/{name}.md"),
    "codex": ("agent.toml", ".codex/agents/{name}.toml"),
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


def agent_value(value: str, key: str, toml: bool) -> str:
    """Escape for the documented template position, preserving simple output."""
    if toml:
        if key == "body":
            # Inside a TOML multiline basic string. Preserve newlines and ordinary quotes.
            value = value.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
            return re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", lambda m: f"\\u{ord(m[0]):04x}", value)
        # Inside a TOML single-line basic string; JSON escapes are compatible here.
        return json.dumps(value, ensure_ascii=False)[1:-1].replace("\x7f", "\\u007f")
    if key == "body":
        return value
    # Plain YAML scalars are readable; quote values with YAML syntax or implicit types.
    if (re.fullmatch(r"[A-Za-z_][A-Za-z0-9_ .,/()@\"'?!-]*", value)
            and value == value.strip()
            and value.lower() not in {"null", "true", "false", "yes", "no", "on", "off"}):
        return value
    return json.dumps(value)


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
    agent: dict | None = None,
) -> str:
    def replace(match: re.Match[str]) -> str:
        kind, name = match.groups()
        if kind == "prompt":
            return prompt_body(name)
        if kind == "agent":
            if agent is None or name not in {"name", "description", "model", "body"}:
                raise ValueError(f"Invalid agent token {match[0]} in {path}")
            value = resolve_model(agent["model_profile"], harness, work, opencode_provider) if name == "model" else agent[name]
            return agent_value(value, name, path.suffix == ".toml")
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
    validate_harnesses(harnesses)
    model_profiles.cache_clear()
    prompt_body.cache_clear()
    agents = load_agents()
    for harness_dir in (TEMPLATES / "overrides").glob("*"):
        if not harness_dir.is_dir() or harness_dir.name not in HARNESSES:
            raise ValueError(f"Unknown override harness: {harness_dir}")
        suffix = Path(AGENT_PATHS[harness_dir.name][0]).suffix
        for path in harness_dir.iterdir():
            if not path.is_file() or path.suffix != suffix or path.stem not in agents:
                raise ValueError(f"Override has no matching agent: {path}")
            if harness_dir.name not in agents[path.stem]["harnesses"]:
                raise ValueError(f"Override targets a disabled harness: {path}")

    # Render and check collisions before replacing an existing successful build.
    outputs = {}
    for harness in harnesses:
        shared_skills = {
            Path(harness) / LAYOUT[harness]["skills"] / p.relative_to(SKILLS)
            for p in SKILLS.rglob("*") if p.is_file()
        }

        def add(relative: Path, rendered: str) -> None:
            destination = Path(harness) / relative
            if destination in outputs or destination in shared_skills or relative == Path(LAYOUT[harness]["base"]):
                raise ValueError(f"Duplicate output: {destination}")
            outputs[destination] = rendered

        for template in sorted(p for p in (TEMPLATES / harness).rglob("*") if p.is_file()):
            add(template.relative_to(TEMPLATES / harness), render_template(template, harness, work, opencode_provider))
        default_name, output_pattern = AGENT_PATHS[harness]
        for name, agent in agents.items():
            if harness not in agent["harnesses"]:
                continue
            override = TEMPLATES / "overrides" / harness / f"{name}{Path(default_name).suffix}"
            template = override if override.is_file() else TEMPLATES / "defaults" / harness / default_name
            add(Path(output_pattern.format(name=name)), render_template(template, harness, work, opencode_provider, agent))

    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir()

    for harness in harnesses:
        output_dir = BUILD / harness
        output_dir.mkdir(parents=True)
        layout = LAYOUT[harness]
        shutil.copy(PROMPTS / "AGENTS.md", output_dir / layout["base"])
        shutil.copytree(SKILLS, output_dir / layout["skills"])

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
        description="Render AI harness configs from provider-native templates."
    )
    parser.add_argument(
        "harnesses",
        nargs="*",
        help="Harnesses to build. Defaults to all.",
    )
    parser.add_argument("--work", action="store_true", help="Use work model mappings.")
    parser.add_argument(
        "--opencode-provider",
        choices=OPENCODE_PROVIDERS,
        help="Override the provider prefix for rendered OpenCode models.",
    )
    args = parser.parse_args(argv)
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
