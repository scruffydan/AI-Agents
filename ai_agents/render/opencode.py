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
    frontmatter: dict[str, object] = {"description": document.description}
    is_mode = document.kind == DocumentKind.MODE
    metadata = override.metadata

    role = metadata.get("role")
    if role is not None:
        frontmatter["role"] = role

    if is_mode:
        frontmatter["mode"] = "primary"
        temperature = metadata.get("temperature")
        if temperature is not None:
            frontmatter["temperature"] = temperature
    elif "mode" in metadata:
        frontmatter["mode"] = metadata["mode"]

    model = metadata.get("model")
    if model is None and not is_mode:
        model = resolved.model
    if model is not None:
        frontmatter["model"] = str(model)

    if is_mode:
        reasoning_effort = metadata.get("reasoning_effort")
        if reasoning_effort is not None:
            frontmatter["reasoningEffort"] = reasoning_effort

    if document.kind not in {DocumentKind.COMMAND, DocumentKind.MODE}:
        merge_settings(frontmatter, resolved.settings)

    for key, value in metadata.items():
        if key in {"role", "mode", "model"}:
            continue
        if is_mode and key in {"temperature", "reasoning_effort", "top_p", "frequency_penalty", "presence_penalty"}:
            continue
        if document.kind == DocumentKind.COMMAND and key != "subtask":
            continue
        frontmatter[normalize_frontmatter_key(key)] = value
    return frontmatter


def merge_settings(frontmatter: dict[str, object], settings: dict[str, object]) -> None:
    for key, value in settings.items():
        frontmatter[normalize_frontmatter_key(key)] = value


def normalize_frontmatter_key(key: str) -> str:
    if key == "reasoning_effort":
        return "reasoningEffort"
    return key
