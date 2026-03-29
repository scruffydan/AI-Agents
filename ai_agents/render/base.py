from __future__ import annotations

from dataclasses import dataclass
import json
import re
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
            rendered = render_yaml_string(str(value))
        lines.append(f"{prefix}{key}: {rendered}")

    return "\n".join(lines)


PLAIN_SCALAR_PATTERN = re.compile(r"^[A-Za-z0-9_./,@`()+-][A-Za-z0-9_./,@`()+\- ]*$")
RESERVED_SCALARS = {"", "null", "true", "false", "yes", "no", "on", "off", "~"}
NUMERIC_PATTERN = re.compile(r"^[-+]?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][-+]?[0-9]+)?$")


def render_yaml_string(value: str) -> str:
    if can_use_plain_scalar(value):
        return value
    return json.dumps(value)


def can_use_plain_scalar(value: str) -> bool:
    if value.strip() != value:
        return False
    lowered = value.lower()
    if lowered in RESERVED_SCALARS:
        return False
    if NUMERIC_PATTERN.match(value):
        return False
    if any(token in value for token in (": ", "\n", '"', "#", "[", "]", "{", "}")):
        return False
    return bool(PLAIN_SCALAR_PATTERN.match(value))


def merge_body(document: Document, override: TargetOverride) -> str:
    parts = [override.body_prepend.strip(), document.body.strip(), override.body_append.strip()]
    return "\n\n".join(part for part in parts if part)


def render_markdown_artifact(relative_path: str, frontmatter: Mapping[str, object], body: str) -> Artifact:
    content = f"---\n{to_yaml(frontmatter)}\n---\n\n{body}\n"
    return Artifact(relative_path=relative_path, content=content)
