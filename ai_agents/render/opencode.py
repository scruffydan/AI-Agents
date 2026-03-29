from __future__ import annotations

from ai_agents.domain.documents import Document, DocumentKind, TargetOverride
from ai_agents.domain.harnesses import HarnessSpec, get_harness
from ai_agents.domain.models import ResolvedModelConfig
from ai_agents.render.base import Artifact, to_yaml


def render_document(document: Document, resolved: ResolvedModelConfig, harness: HarnessSpec | None = None) -> Artifact | None:
    spec = harness or get_harness("opencode")
    override = document.targets.get(spec.name)
    if override is None or not override.enabled:
        return None

    output_dir = spec.output_dir_for(document.kind)
    if output_dir is None:
        raise ValueError(f"OpenCode does not support kind {document.kind.value!r}")

    frontmatter = build_frontmatter(document, override, resolved)
    body = merge_body(document, override)
    content = f"---\n{to_yaml(frontmatter)}\n---\n\n{body}\n"
    return Artifact(relative_path=f"{spec.output_layout.root}/{output_dir}/{document.name}.md", content=content)


def build_frontmatter(
    document: Document,
    override: TargetOverride,
    resolved: ResolvedModelConfig,
) -> dict[str, object]:
    frontmatter: dict[str, object] = {"description": document.description, "model": resolved.model}

    role = override.metadata.get("role")
    if role is not None:
        frontmatter["role"] = role

    if document.kind == DocumentKind.MODE:
        frontmatter["mode"] = "primary"
    elif "mode" in override.metadata:
        frontmatter["mode"] = override.metadata["mode"]

    for key, value in resolved.settings.items():
        frontmatter[key] = value
    for key, value in override.metadata.items():
        if key in {"role", "mode"}:
            continue
        if key == "model":
            continue
        frontmatter[key] = value
    return frontmatter


def merge_body(document: Document, override: TargetOverride) -> str:
    parts = [override.body_prepend.strip(), document.body.strip(), override.body_append.strip()]
    return "\n\n".join(part for part in parts if part)
