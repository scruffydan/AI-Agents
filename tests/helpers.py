from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def fixtures_dir() -> Path:
    return repo_root() / "tests" / "fixtures"
