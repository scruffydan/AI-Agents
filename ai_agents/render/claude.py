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
    relative_path = render_path(document, harness, output_dir)
    return render_markdown_artifact(relative_path, frontmatter, body)


def render_path(document: Document, harness: HarnessSpec, output_dir: str) -> str:
    if document.kind == DocumentKind.COMMAND:
        return f"{harness.output_layout.root}/{output_dir}/{document.name}/SKILL.md"
    return f"{harness.output_layout.root}/{output_dir}/{document.name}.md"


def build_frontmatter(
    document: Document,
    override: TargetOverride,
    resolved: ResolvedModelConfig,
) -> dict[str, object]:
    frontmatter: dict[str, object] = {}

    if document.kind in {DocumentKind.SUBAGENT, DocumentKind.COMMAND}:
        frontmatter["name"] = document.name
    frontmatter["description"] = document.description

    if "tools" in override.metadata:
        key = "tools" if document.kind == DocumentKind.SUBAGENT else "allowed-tools"
        frontmatter[key] = override.metadata["tools"]

    model = override.metadata.get("model")
    if model is None and document.kind == DocumentKind.SUBAGENT:
        model = resolved.model
    if model is not None:
        frontmatter["model"] = str(model)

    if "effort" in override.metadata:
        frontmatter["effort"] = override.metadata["effort"]
    return frontmatter
