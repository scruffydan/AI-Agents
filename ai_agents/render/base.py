from __future__ import annotations

from dataclasses import dataclass
import json
from collections.abc import Mapping

from ai_agents.domain.documents import Document, TargetOverride


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


def merge_body(document: Document, override: TargetOverride) -> str:
    parts = [override.body_prepend.strip(), document.body.strip(), override.body_append.strip()]
    return "\n\n".join(part for part in parts if part)


def render_markdown_artifact(relative_path: str, frontmatter: Mapping[str, object], body: str) -> Artifact:
    content = f"---\n{to_yaml(frontmatter)}\n---\n\n{body}\n"
    return Artifact(relative_path=relative_path, content=content)
