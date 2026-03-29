from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any

from ai_agents.content.includes import expand_includes
from ai_agents.domain.documents import Document, DocumentKind, TargetOverride


def parse_document(path: Path, include_dir: Path | None = None) -> Document:
    frontmatter, body = split_frontmatter(path.read_text(), path)
    data = tomllib.loads(frontmatter)

    if "kind" in data and "targets" in data:
        return parse_v2_document(path, data, body, include_dir)
    return parse_legacy_document(path, data, body, include_dir)


def parse_v2_document(path: Path, data: dict[str, Any], body: str, include_dir: Path | None) -> Document:
    description = require_string(data, "description", path)
    model_profile = require_string(data, "model_profile", path)
    kind_value = require_string(data, "kind", path)
    try:
        kind = DocumentKind(kind_value)
    except ValueError as exc:
        expected = ", ".join(kind.value for kind in DocumentKind)
        raise ValueError(f"{path}: invalid kind {kind_value!r}; expected one of: {expected}") from exc

    shared_metadata = require_table(data, "shared", default={}, path=path)
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
        shared_metadata=shared_metadata,
        targets=targets,
        source_path=path,
    )


def parse_legacy_document(path: Path, data: dict[str, Any], body: str, include_dir: Path | None) -> Document:
    description = require_string(data, "description", path)
    kind_value = require_string(data, "type", path)
    try:
        kind = DocumentKind(kind_value)
    except ValueError as exc:
        expected = ", ".join(kind.value for kind in DocumentKind if kind != DocumentKind.SKILL and kind != DocumentKind.BASE)
        raise ValueError(f"{path}: invalid legacy type {kind_value!r}; expected one of: {expected}") from exc

    claude_values = require_table(data, "claude", default={}, path=path)
    opencode_values = require_table(data, "opencode", default={}, path=path)
    model_profile = infer_legacy_model_profile(path.stem, kind, claude_values, opencode_values)

    targets: dict[str, TargetOverride] = {
        "opencode": TargetOverride(metadata=normalize_legacy_metadata(opencode_values)),
        "codex": TargetOverride(metadata=default_codex_metadata(kind)),
    }

    if kind != DocumentKind.MODE or claude_values:
        targets["claude"] = TargetOverride(metadata=normalize_legacy_metadata(claude_values))
    elif kind == DocumentKind.MODE:
        targets["claude"] = TargetOverride(metadata={})

    content = body.strip()
    if include_dir is not None:
        content = expand_includes(content, include_dir)

    return Document(
        name=path.stem,
        description=description,
        kind=kind,
        body=content,
        model_profile=model_profile,
        shared_metadata={},
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
    enabled = require_bool(known, "enabled", default=True, path=path, scope=f"targets.{target_name}")
    body_prepend = require_string(known, "body_prepend", default="", path=path, scope=f"targets.{target_name}")
    body_append = require_string(known, "body_append", default="", path=path, scope=f"targets.{target_name}")
    partials = require_string_list(known, "partials", default=(), path=path, scope=f"targets.{target_name}")

    metadata = {
        key: value
        for key, value in known.items()
        if key not in {"enabled", "body_prepend", "body_append", "partials"}
    }
    return TargetOverride(
        enabled=enabled,
        metadata=metadata,
        body_prepend=body_prepend,
        body_append=body_append,
        partials=tuple(partials),
    )


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


def require_string_list(
    data: dict[str, Any],
    key: str,
    path: Path,
    scope: str,
    default: tuple[str, ...],
) -> tuple[str, ...]:
    if key not in data:
        return default
    value = data[key]
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"{path}: field {scope}.{key} must be a list of non-empty strings")
    return tuple(value)


LEGACY_PROFILE_OVERRIDES = {
    "brainstorm": "creative",
    "thorough-plan": "planner",
    "code-full-review": "deep_review",
    "code-performance": "deep_review",
    "code-readability": "deep_review",
    "code-redundancy": "deep_review",
    "code-security": "deep_review",
    "code-simplifier": "deep_review",
    "sidebar": "deep_review",
    "docs-fetcher": "default",
    "explore": "default",
    "git-commit": "default",
}


def infer_legacy_model_profile(
    name: str,
    kind: DocumentKind,
    claude_values: dict[str, Any],
    opencode_values: dict[str, Any],
) -> str:
    if name in LEGACY_PROFILE_OVERRIDES:
        return LEGACY_PROFILE_OVERRIDES[name]

    if kind == DocumentKind.MODE:
        return "planner"

    claude_model = str(claude_values.get("model", ""))
    opencode_reasoning = str(opencode_values.get("reasoningEffort", ""))
    if "opus" in claude_model or opencode_reasoning == "high":
        return "deep_review"
    return "default"


def normalize_legacy_metadata(values: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in values.items():
        normalized[to_snake_case(key)] = normalize_legacy_value(value)
    return normalized


def normalize_legacy_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {to_snake_case(str(key)): normalize_legacy_value(nested) for key, nested in value.items()}
    if isinstance(value, list):
        return [normalize_legacy_value(item) for item in value]
    return value


def to_snake_case(value: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", value).lower()


def default_codex_metadata(kind: DocumentKind) -> dict[str, Any]:
    if kind == DocumentKind.SUBAGENT:
        return {"sandbox": "workspace-write", "approval_policy": "on-request"}
    if kind == DocumentKind.MODE:
        return {"sandbox": "read-only", "approval_policy": "on-request"}
    return {"sandbox": "workspace-write", "approval_policy": "on-request"}
