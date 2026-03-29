from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_agents.domain.harnesses import OutputComponent


@dataclass(frozen=True)
class InstallAction:
    harness: str
    component: OutputComponent
    label: str
    source: Path
    destination: Path
    kind: str
    status: str


@dataclass(frozen=True)
class InstallPlan:
    build_dir: Path
    actions: tuple[InstallAction, ...]
