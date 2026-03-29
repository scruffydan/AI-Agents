from __future__ import annotations

from ai_agents.domain.documents import Document, DocumentKind, TargetOverride
from ai_agents.domain.harnesses import HarnessSpec, get_harness
from ai_agents.domain.models import ResolvedModelConfig
from ai_agents.render.base import Artifact, merge_body, render_markdown_artifact


def render_document(document: Document, resolved: ResolvedModelConfig, harness: HarnessSpec | None = None) -> Artifact | None:
    spec = harness or get_harness("claude")
    override = document.targets.get(spec.name)
    if override is None or not override.enabled:
        return None

    output_dir = spec.output_dir_for(document.kind)
    if output_dir is None:
        return None

    frontmatter = build_frontmatter(document, override, resolved)
    body = merge_body(document, override)
    return render_markdown_artifact(f"{spec.output_layout.root}/{output_dir}/{document.name}.md", frontmatter, body)


def build_frontmatter(
    document: Document,
    override: TargetOverride,
    resolved: ResolvedModelConfig,
) -> dict[str, object]:
    frontmatter: dict[str, object] = {"description": document.description}

    if document.kind == DocumentKind.SUBAGENT:
        frontmatter["name"] = document.name
    if document.kind in {DocumentKind.SUBAGENT, DocumentKind.COMMAND, DocumentKind.MODE}:
        frontmatter["model"] = normalize_claude_model(str(override.metadata.get("model") or resolved.model))

    if "tools" in override.metadata:
        frontmatter["tools"] = override.metadata["tools"]
    if "effort" in override.metadata:
        frontmatter["effort"] = override.metadata["effort"]
    elif resolved.settings.get("reasoning_effort"):
        frontmatter["effort"] = resolved.settings["reasoning_effort"]
    return frontmatter


def normalize_claude_model(model: str) -> str:
    if model.startswith("claude-opus"):
        return "opus"
    if model.startswith("claude-sonnet"):
        return "sonnet"
    if model.startswith("claude-haiku"):
        return "haiku"
    return model
