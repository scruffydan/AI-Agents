from __future__ import annotations

import json

from ai_agents.domain.documents import Document, DocumentKind, TargetOverride
from ai_agents.domain.harnesses import HarnessSpec, get_harness
from ai_agents.domain.models import ResolvedModelConfig
from ai_agents.render.base import Artifact, merge_body, render_markdown_artifact


def render_document(document: Document, resolved: ResolvedModelConfig, harness: HarnessSpec | None = None) -> Artifact | None:
    spec = harness or get_harness("codex")
    override = document.targets.get(spec.name)
    if override is None or not override.enabled:
        return None

    if document.kind == DocumentKind.SUBAGENT:
        return render_subagent(document, override, resolved, spec)
    if document.kind in {DocumentKind.COMMAND, DocumentKind.MODE}:
        return render_prompt_skill(document, override, spec)
    return None


def render_subagent(
    document: Document,
    override: TargetOverride,
    resolved: ResolvedModelConfig,
    spec: HarnessSpec,
) -> Artifact:
    body = merge_body(document, override)
    lines = [
        f"name = {toml_string(document.name)}",
        f"description = {toml_string(document.description)}",
        f"model = {toml_string(str(override.metadata.get('model') or resolved.model))}",
    ]

    sandbox_mode = override.metadata.get("sandbox") or resolved.settings.get("sandbox")
    if sandbox_mode:
        lines.append(f"sandbox_mode = {toml_string(str(sandbox_mode))}")

    reasoning_effort = resolved.settings.get("reasoning_effort")
    if reasoning_effort:
        lines.append(f"model_reasoning_effort = {toml_string(str(reasoning_effort))}")

    lines.append(f"developer_instructions = {toml_multiline(body)}")
    content = "\n".join(lines) + "\n"
    output_dir = spec.output_dir_for(DocumentKind.SUBAGENT)
    return Artifact(relative_path=f"{spec.output_layout.root}/{output_dir}/{document.name}.toml", content=content)


def render_prompt_skill(document: Document, override: TargetOverride, spec: HarnessSpec) -> Artifact:
    skill_name = codex_skill_name(document)
    frontmatter = {
        "name": skill_name,
        "description": document.description,
    }
    body = merge_body(document, override)
    output_dir = spec.output_dir_for(document.kind)
    return render_markdown_artifact(f"{spec.output_layout.root}/{output_dir}/{skill_name}/SKILL.md", frontmatter, body)


def codex_skill_name(document: Document) -> str:
    prefix = "command" if document.kind == DocumentKind.COMMAND else "mode"
    return f"{prefix}-{document.name}"


def toml_string(value: str) -> str:
    return json.dumps(value)


def toml_multiline(value: str) -> str:
    escaped = value.replace('"""', '\"\"\"')
    return f'"""\n{escaped}\n"""'
