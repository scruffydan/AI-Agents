from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content)


def resolve_relative_to(root: Path, relative: str | Path, label: str) -> Path:
    root = root.resolve()
    candidate = Path(relative)
    if candidate.is_absolute():
        raise ValueError(f"{label} must stay within {root}")

    resolved = (root / candidate).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"{label} must stay within {root}")
    return resolved


def ensure_no_symlinks(root: Path) -> None:
    if not root.exists():
        return
    if root.is_symlink():
        raise ValueError(f"symlinks are not allowed in {root}")

    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlinks are not allowed in {root}: {path}")


def copy_dir(source: Path, destination: Path) -> None:
    ensure_dir(destination.parent)
    shutil.copytree(source, destination)


def replace_dir(source: Path, destination: Path) -> None:
    if source == destination:
        raise ValueError("source and destination must be different")

    ensure_dir(destination.parent)
    if destination.is_symlink():
        raise ValueError(f"refusing to replace symlink directory {destination}")
    if destination.exists() and not destination.is_dir():
        raise ValueError(f"refusing to replace non-directory path {destination}")
    if destination.exists():
        shutil.rmtree(destination)
    source.replace(destination)


def replace_tree(source: Path, destination: Path) -> None:
    staged = destination.parent / f".{destination.name}.tmp-{uuid4().hex}"
    copy_dir(source, staged)
    try:
        replace_dir(staged, destination)
    finally:
        if staged.exists():
            shutil.rmtree(staged)


def replace_file(source: Path, destination: Path, mode: int | None = None) -> None:
    ensure_dir(destination.parent)
    if destination.is_symlink():
        raise ValueError(f"refusing to replace symlink file {destination}")
    if destination.exists() and destination.is_dir():
        raise ValueError(f"refusing to replace directory with file {destination}")

    staged = destination.parent / f".{destination.name}.tmp-{uuid4().hex}"
    shutil.copy2(source, staged)
    try:
        if mode is not None:
            staged.chmod(mode)
        staged.replace(destination)
    finally:
        if staged.exists():
            staged.unlink()
