from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResolvedModelConfig:
    profile_name: str
    environment: str
    harness: str
    provider: str | None
    model_name: str
    model: str
    settings: dict[str, Any] = field(default_factory=dict)
