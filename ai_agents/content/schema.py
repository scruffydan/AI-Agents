from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from ai_agents.content.includes import expand_includes
from ai_agents.domain.documents import Document, DocumentKind, TargetOverride


def parse_document(path: Path, include_dir: Path | None = None) -> Document:
    frontmatter, body = split_frontmatter(path.read_text(), path)
    data = tomllib.loads(frontmatter)
    return parse_v2_document(path, data, body, include_dir)


def parse_v2_document(path: Path, data: dict[str, Any], body: str, include_dir: Path | None) -> Document:
    description = require_string(data, "description", path)
    model_profile = require_string(data, "model_profile", path)
    kind_value = require_string(data, "kind", path)
    reject_unsupported_key(data, "shared", path, scope="root")
    try:
        kind = DocumentKind(kind_value)
    except ValueError as exc:
        expected = ", ".join(kind.value for kind in DocumentKind)
        raise ValueError(f"{path}: invalid kind {kind_value!r}; expected one of: {expected}") from exc

    targets_raw = require_table(data, "targets", default={}, path=path)
    targets = {
        target_name: parse_target_override(path, target_name, values)
        for target_name, values in targets_raw.items()
    }

    content = body.strip()
    if include_dir is not None:
        content = expand_includes(content, include_dir)

    return Document(
        name=path.stem,
        description=description,
        kind=kind,
        body=content,
        model_profile=model_profile,
        targets=targets,
        source_path=path,
    )


def split_frontmatter(raw: str, path: Path) -> tuple[str, str]:
    normalized = raw.replace("\r\n", "\n")
    if not normalized.startswith("+++\n"):
        raise ValueError(f"{path}: missing opening TOML frontmatter delimiter")

    remainder = normalized.removeprefix("+++\n")
    marker = "\n+++\n"
    index = remainder.find(marker)
    if index < 0:
        raise ValueError(f"{path}: missing closing TOML frontmatter delimiter")

    return remainder[:index], remainder[index + len(marker) :]


def parse_target_override(path: Path, target_name: str, values: Any) -> TargetOverride:
    if not isinstance(values, dict):
        raise ValueError(f"{path}: targets.{target_name} must be a table")

    known = dict(values)
    reject_unsupported_key(known, "partials", path, scope=f"targets.{target_name}")
    enabled = require_bool(known, "enabled", default=True, path=path, scope=f"targets.{target_name}")
    body_prepend = require_string(known, "body_prepend", default="", path=path, scope=f"targets.{target_name}")
    body_append = require_string(known, "body_append", default="", path=path, scope=f"targets.{target_name}")

    metadata = {
        key: value
        for key, value in known.items()
        if key not in {"enabled", "body_prepend", "body_append"}
    }
    return TargetOverride(
        enabled=enabled,
        metadata=metadata,
        body_prepend=body_prepend,
        body_append=body_append,
    )


def reject_unsupported_key(data: dict[str, Any], key: str, path: Path, scope: str) -> None:
    if key in data:
        location = key if scope == "root" else f"{scope}.{key}"
        raise ValueError(f"{path}: field {location} is not supported")


def require_string(data: dict[str, Any], key: str, path: Path, scope: str | None = None, default: str | None = None) -> str:
    if key not in data:
        if default is not None:
            return default
        location = scope or "root"
        raise ValueError(f"{path}: missing required string field {location}.{key}" if scope else f"{path}: missing required string field {key}")
    value = data[key]
    if not isinstance(value, str) or not value.strip():
        location = f"{scope}.{key}" if scope else key
        raise ValueError(f"{path}: field {location} must be a non-empty string")
    return value


def require_bool(data: dict[str, Any], key: str, path: Path, scope: str, default: bool) -> bool:
    if key not in data:
        return default
    value = data[key]
    if not isinstance(value, bool):
        raise ValueError(f"{path}: field {scope}.{key} must be a boolean")
    return value


def require_table(data: dict[str, Any], key: str, default: dict[str, Any], path: Path) -> dict[str, Any]:
    value = data.get(key, default)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: field {key} must be a table")
    return value
