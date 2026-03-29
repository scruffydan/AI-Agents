from __future__ import annotations

import shutil
from pathlib import Path


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content)


def reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_file(source: Path, destination: Path) -> None:
    ensure_dir(destination.parent)
    shutil.copy2(source, destination)


def copy_dir(source: Path, destination: Path) -> None:
    ensure_dir(destination.parent)
    shutil.copytree(source, destination, dirs_exist_ok=True)
