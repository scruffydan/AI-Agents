from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BuildOptions:
    repo_root: Path
    output_dir: Path | None = None
    selected_harnesses: tuple[str, ...] = ()
    environment: str = "default"
    include_skills: bool = True
    include_base_files: bool = True


@dataclass(frozen=True)
class InstallOptions:
    repo_root: Path
    build_dir: Path | None = None
    selected_harnesses: tuple[str, ...] = ()
    force: bool = False
    skip_build: bool = False
    environment: str = "default"
