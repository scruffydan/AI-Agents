from __future__ import annotations

from ai_agents.domain.documents import Document, DocumentKind, TargetOverride
from ai_agents.domain.harnesses import HarnessSpec
from ai_agents.domain.models import ResolvedModelConfig
from ai_agents.render.base import Artifact, merge_body, render_markdown_artifact


def render_document(document: Document, resolved: ResolvedModelConfig, harness: HarnessSpec) -> Artifact | None:
    override = document.targets.get(harness.name)
    if override is None or not override.enabled:
        return None

    output_dir = harness.output_dir_for(document.kind)
    if output_dir is None:
        raise ValueError(f"OpenCode does not support kind {document.kind.value!r}")

    frontmatter = build_frontmatter(document, override, resolved)
    body = merge_body(document, override)
    return render_markdown_artifact(f"{harness.output_layout.root}/{output_dir}/{document.name}.md", frontmatter, body)


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
