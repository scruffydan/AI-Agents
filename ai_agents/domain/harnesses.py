from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from ai_agents.domain.documents import DocumentKind


@dataclass
class OutputLayout:
    root: str
    kind_directories: dict[DocumentKind, str]
    skills_dir: str
    commands_as_skills: bool = False


@dataclass(frozen=True)
class InstallEntry:
    source: Path
    destination: Path
    kind: Literal["tree", "file"]
    label: str


@dataclass
class HarnessSpec:
    name: str
    default_selected: bool
    supports_modes: bool
    supported_kinds: tuple[DocumentKind, ...]
    output_layout: OutputLayout
    install_target: Path
    install_entries: tuple[InstallEntry, ...]
    base_filename: str
    capabilities: tuple[str, ...]
    supported_metadata_keys: frozenset[str]

    def output_dir_for(self, kind: DocumentKind) -> str | None:
        return self.output_layout.kind_directories.get(kind)


HARNESS_REGISTRY: dict[str, HarnessSpec] = {
    "opencode": HarnessSpec(
        name="opencode",
        default_selected=True,
        supports_modes=True,
        supported_kinds=(
            DocumentKind.SUBAGENT,
            DocumentKind.COMMAND,
            DocumentKind.MODE,
            DocumentKind.SKILL,
            DocumentKind.BASE,
        ),
        output_layout=OutputLayout(
            root="opencode",
            kind_directories={
                DocumentKind.SUBAGENT: "agent",
                DocumentKind.COMMAND: "command",
                DocumentKind.MODE: "agent",
                DocumentKind.SKILL: "skill",
                DocumentKind.BASE: ".",
            },
            skills_dir="skill",
        ),
        install_target=Path.home() / ".config" / "opencode",
        install_entries=(
            InstallEntry(
                source=Path("."),
                destination=Path(".config") / "opencode",
                kind="tree",
                label="opencode",
            ),
        ),
        base_filename="AGENTS.md",
        capabilities=("modes", "permissions", "skills"),
        supported_metadata_keys=frozenset(
            {
                "role",
                "mode",
                "model",
                "permission",
                "tools",
                "reasoning_effort",
                "temperature",
                "top_p",
                "frequency_penalty",
                "presence_penalty",
                "subtask",
            }
        ),
    ),
    "claude": HarnessSpec(
        name="claude",
        default_selected=False,
        supports_modes=True,
        supported_kinds=(
            DocumentKind.SUBAGENT,
            DocumentKind.COMMAND,
            DocumentKind.MODE,
            DocumentKind.SKILL,
            DocumentKind.BASE,
        ),
        output_layout=OutputLayout(
            root="claude",
            kind_directories={
                DocumentKind.SUBAGENT: "agents",
                DocumentKind.COMMAND: "commands",
                DocumentKind.MODE: "commands",
                DocumentKind.SKILL: "skills",
                DocumentKind.BASE: ".",
            },
            skills_dir="skills",
        ),
        install_target=Path.home() / ".claude",
        install_entries=(
            InstallEntry(
                source=Path("."),
                destination=Path(".claude"),
                kind="tree",
                label="claude",
            ),
        ),
        base_filename="CLAUDE.md",
        capabilities=("skills", "tools"),
        supported_metadata_keys=frozenset({"role", "tools", "model"}),
    ),
    "codex": HarnessSpec(
        name="codex",
        default_selected=False,
        supports_modes=True,
        supported_kinds=(
            DocumentKind.SUBAGENT,
            DocumentKind.COMMAND,
            DocumentKind.MODE,
            DocumentKind.SKILL,
            DocumentKind.BASE,
        ),
        output_layout=OutputLayout(
            root="codex",
            kind_directories={
                DocumentKind.SUBAGENT: ".codex/agents",
                DocumentKind.COMMAND: ".agents/skills",
                DocumentKind.MODE: ".agents/skills",
                DocumentKind.SKILL: ".agents/skills",
                DocumentKind.BASE: ".",
            },
            skills_dir=".agents/skills",
            commands_as_skills=True,
        ),
        install_target=Path.home() / ".codex",
        install_entries=(
            InstallEntry(
                source=Path(".codex"),
                destination=Path(".codex"),
                kind="tree",
                label="codex agents",
            ),
            InstallEntry(
                source=Path(".agents") / "skills",
                destination=Path(".agents") / "skills",
                kind="tree",
                label="codex skills",
            ),
            InstallEntry(
                source=Path("AGENTS.md"),
                destination=Path(".codex") / "AGENTS.md",
                kind="file",
                label="codex base instructions",
            ),
        ),
        base_filename="AGENTS.md",
        capabilities=("sandbox", "approval_policy", "skills"),
        supported_metadata_keys=frozenset({"role", "model", "sandbox", "approval_policy"}),
    ),
}


def all_harnesses() -> tuple[HarnessSpec, ...]:
    return tuple(HARNESS_REGISTRY.values())


def default_harnesses() -> tuple[HarnessSpec, ...]:
    return tuple(spec for spec in HARNESS_REGISTRY.values() if spec.default_selected)


def get_harness(name: str) -> HarnessSpec:
    try:
        return HARNESS_REGISTRY[name]
    except KeyError as exc:
        known = ", ".join(sorted(HARNESS_REGISTRY))
        raise ValueError(f"unknown harness {name!r}; expected one of: {known}") from exc


def select_harnesses(requested: list[str] | tuple[str, ...] | None, include_all: bool) -> tuple[HarnessSpec, ...]:
    if include_all:
        return all_harnesses()

    if not requested:
        return default_harnesses()

    selected: list[HarnessSpec] = []
    seen: set[str] = set()
    for name in requested:
        if name in seen:
            continue
        seen.add(name)
        selected.append(get_harness(name))
    return tuple(selected)
