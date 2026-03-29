from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class DocumentKind(str, Enum):
    SUBAGENT = "subagent"
    COMMAND = "command"
    MODE = "mode"
    SKILL = "skill"
    BASE = "base"


@dataclass(frozen=True)
class TargetOverride:
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
    body_prepend: str = ""
    body_append: str = ""
    partials: tuple[str, ...] = ()


@dataclass(frozen=True)
class Document:
    name: str
    description: str
    kind: DocumentKind
    body: str
    model_profile: str
    shared_metadata: dict[str, Any] = field(default_factory=dict)
    targets: dict[str, TargetOverride] = field(default_factory=dict)
    source_path: Path | None = None
