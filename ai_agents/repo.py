from __future__ import annotations

from pathlib import Path


def find_repo_root(start: Path | None = None) -> Path:
    current = (start or Path(__file__)).resolve()
    if current.is_file():
        current = current.parent

    for candidate in (current, *current.parents):
        if _looks_like_repo_root(candidate):
            return candidate

    raise ValueError(f"could not find repo root from {current}")


def _looks_like_repo_root(path: Path) -> bool:
    return (path / ".git").exists() and (path / "source" / "prompts").is_dir()
