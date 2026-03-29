from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from ai_agents.domain.documents import DocumentKind


OutputComponent = Literal["base", "documents", "skills"]


@dataclass
class OutputLayout:
    root: str
    kind_directories: dict[DocumentKind, str]


@dataclass(frozen=True)
class InstallEntry:
    source: Path
    destination: Path
    kind: Literal["tree", "file"]
    component: OutputComponent
    label: str


@dataclass
class HarnessSpec:
    name: str
    default_selected: bool
    supported_kinds: tuple[DocumentKind, ...]
    output_layout: OutputLayout
    install_entries: tuple[InstallEntry, ...]
    base_filename: str
    supported_metadata_keys: frozenset[str]

    def output_dir_for(self, kind: DocumentKind) -> str | None:
        return self.output_layout.kind_directories.get(kind)

    def component_for_kind(self, kind: DocumentKind) -> OutputComponent:
        if kind == DocumentKind.BASE:
            return "base"
        if kind == DocumentKind.SKILL:
            return "skills"
        return "documents"

    def base_output_path(self) -> Path:
        return Path(self.output_layout.root) / self.base_filename

    def skill_output_path(self, skill_name: str) -> Path:
        skill_dir = self.output_dir_for(DocumentKind.SKILL)
        if skill_dir is None:
            raise ValueError(f"harness {self.name!r} does not define a skill output directory")
        return Path(self.output_layout.root) / skill_dir / skill_name

    def install_entries_for(self, components: tuple[OutputComponent, ...] = ()) -> tuple[InstallEntry, ...]:
        if not components:
            return self.install_entries
        selected = set(components)
        return tuple(entry for entry in self.install_entries if entry.component in selected)


HARNESS_REGISTRY: dict[str, HarnessSpec] = {
    "opencode": HarnessSpec(
        name="opencode",
        default_selected=True,
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
        ),
        install_entries=(
            InstallEntry(
                source=Path("AGENTS.md"),
                destination=Path(".config") / "opencode" / "AGENTS.md",
                kind="file",
                component="base",
                label="opencode base instructions",
            ),
            InstallEntry(
                source=Path("agent"),
                destination=Path(".config") / "opencode" / "agent",
                kind="tree",
                component="documents",
                label="opencode agents",
            ),
            InstallEntry(
                source=Path("command"),
                destination=Path(".config") / "opencode" / "command",
                kind="tree",
                component="documents",
                label="opencode commands",
            ),
            InstallEntry(
                source=Path("skill"),
                destination=Path(".config") / "opencode" / "skill",
                kind="tree",
                component="skills",
                label="opencode skills",
            ),
        ),
        base_filename="AGENTS.md",
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
        ),
        install_entries=(
            InstallEntry(
                source=Path("CLAUDE.md"),
                destination=Path(".claude") / "CLAUDE.md",
                kind="file",
                component="base",
                label="claude base instructions",
            ),
            InstallEntry(
                source=Path("agents"),
                destination=Path(".claude") / "agents",
                kind="tree",
                component="documents",
                label="claude agents",
            ),
            InstallEntry(
                source=Path("commands"),
                destination=Path(".claude") / "commands",
                kind="tree",
                component="documents",
                label="claude commands",
            ),
            InstallEntry(
                source=Path("skills"),
                destination=Path(".claude") / "skills",
                kind="tree",
                component="skills",
                label="claude skills",
            ),
        ),
        base_filename="CLAUDE.md",
        supported_metadata_keys=frozenset({"role", "tools", "model"}),
    ),
    "codex": HarnessSpec(
        name="codex",
        default_selected=False,
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
        ),
        install_entries=(
            InstallEntry(
                source=Path(".codex"),
                destination=Path(".codex"),
                kind="tree",
                component="documents",
                label="codex agents",
            ),
            InstallEntry(
                source=Path(".agents") / "skills",
                destination=Path(".agents") / "skills",
                kind="tree",
                component="skills",
                label="codex skills",
            ),
            InstallEntry(
                source=Path("AGENTS.md"),
                destination=Path(".codex") / "AGENTS.md",
                kind="file",
                component="base",
                label="codex base instructions",
            ),
        ),
        base_filename="AGENTS.md",
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
