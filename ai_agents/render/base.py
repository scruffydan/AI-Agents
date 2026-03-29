from __future__ import annotations

from dataclasses import dataclass
import json
from collections.abc import Mapping


@dataclass(frozen=True)
class Artifact:
    relative_path: str
    content: str


def to_yaml(data: Mapping[str, object], indent: int = 0) -> str:
    lines: list[str] = []
    prefix = "  " * indent

    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(to_yaml(value, indent + 1))
            continue
        if isinstance(value, bool):
            rendered = str(value).lower()
        elif isinstance(value, (int, float)):
            rendered = str(value)
        elif value is None:
            rendered = "null"
        else:
            rendered = json.dumps(str(value))
        lines.append(f"{prefix}{key}: {rendered}")

    return "\n".join(lines)
