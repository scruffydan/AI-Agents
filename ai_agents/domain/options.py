from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_agents.domain.harnesses import OutputComponent


@dataclass(frozen=True)
class BuildOptions:
    repo_root: Path
    output_dir: Path | None = None
    selected_harnesses: tuple[str, ...] = ()
    environment: str = "default"
    include_skills: bool = True


@dataclass(frozen=True)
class InstallOptions:
    repo_root: Path
    build_dir: Path | None = None
    selected_harnesses: tuple[str, ...] = ()
    selected_components: tuple[OutputComponent, ...] = ()
    force: bool = False
    skip_build: bool = False
    dry_run: bool = False
    environment: str = "default"
    home_dir: Path | None = None
