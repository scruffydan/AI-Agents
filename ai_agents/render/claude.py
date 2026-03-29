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
        return None

    frontmatter = build_frontmatter(document, override, resolved)
    body = merge_body(document, override)
    return render_markdown_artifact(f"{harness.output_layout.root}/{output_dir}/{document.name}.md", frontmatter, body)


def build_frontmatter(
    document: Document,
    override: TargetOverride,
    resolved: ResolvedModelConfig,
) -> dict[str, object]:
    frontmatter: dict[str, object] = {}

    if document.kind == DocumentKind.SUBAGENT:
        frontmatter["name"] = document.name
    frontmatter["description"] = document.description

    if "tools" in override.metadata:
        frontmatter["tools"] = override.metadata["tools"]

    model = override.metadata.get("model")
    if model is None and document.kind == DocumentKind.SUBAGENT:
        model = resolved.model
    if model is not None:
        frontmatter["model"] = str(model)

    if "effort" in override.metadata:
        frontmatter["effort"] = override.metadata["effort"]
    return frontmatter
