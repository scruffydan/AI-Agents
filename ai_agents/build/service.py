from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from uuid import uuid4

from ai_agents.content.loader import load_validated_documents
from ai_agents.domain.documents import Document
from ai_agents.domain.harnesses import HarnessSpec, OutputComponent, select_harnesses
from ai_agents.domain.manifest import BuildManifest, ManifestArtifact, relative_to_root
from ai_agents.domain.models import ResolvedModelConfig
from ai_agents.domain.options import BuildOptions
from ai_agents.fs import copy_dir, ensure_dir, ensure_no_symlinks, replace_dir, write_text
from ai_agents.profiles.resolver import load_model_profiles, resolve_model_profile
from ai_agents.render import claude, codex, opencode
from ai_agents.render.base import Artifact


@dataclass(frozen=True)
class BuildReport:
    repo_root: Path
    output_dir: Path
    environment: str
    harnesses: tuple[HarnessSpec, ...]
    document_count: int
    artifact_count: int
    skill_count: int
    base_file_count: int
    manifest_path: Path


Renderer = Callable[[Document, ResolvedModelConfig, HarnessSpec], Artifact | None]


RENDERERS: dict[str, Renderer] = {
    "opencode": opencode.render_document,
    "claude": claude.render_document,
    "codex": codex.render_document,
}


def build_project(options: BuildOptions) -> BuildReport:
    repo_root = options.repo_root.resolve()
    output_dir = normalize_output_dir(repo_root, options.output_dir)
    harnesses = select_harnesses(options.selected_harnesses, include_all=False)
    prompts_dir = repo_root / "source" / "prompts"
    skills_dir = repo_root / "source" / "skills"
    base_instructions = prompts_dir / "AGENTS.md"
    ensure_no_symlinks(skills_dir)
    documents = load_validated_documents(prompts_dir, include_dir=prompts_dir, harnesses=harnesses)

    profiles = load_model_profiles(repo_root / "source" / "model-profiles.toml")
    staging_dir = stage_output_dir(output_dir)

    try:
        manifest_records: list[ManifestArtifact] = []
        artifact_count = 0
        for document in documents:
            for harness in harnesses:
                if harness.name not in document.targets:
                    continue
                resolved = resolve_model_profile(profiles, document.model_profile, options.environment, harness.name)
                artifact = render_for_harness(document, harness, resolved)
                if artifact is None:
                    continue
                write_text(staging_dir / artifact.relative_path, artifact.content)
                record_manifest_artifact(
                    manifest_records,
                    repo_root=repo_root,
                    harness=harness.name,
                    component=harness.component_for_kind(document.kind),
                    relative_output_path=artifact.relative_path,
                    source_path=document.source_path,
                    kind=document.kind.value,
                    model_profile=document.model_profile,
                )
                artifact_count += 1

        base_file_count = write_base_files(base_instructions, staging_dir, harnesses, repo_root, manifest_records)
        skill_count = copy_skills(skills_dir, staging_dir, harnesses, repo_root, manifest_records)
        write_manifest(repo_root, output_dir, options.environment, harnesses, staging_dir, documents, manifest_records)
        replace_dir(staging_dir, output_dir)
    except Exception:
        if staging_dir.exists():
            shutil.rmtree(staging_dir)
        raise

    return BuildReport(
        repo_root=repo_root,
        output_dir=output_dir,
        environment=options.environment,
        harnesses=harnesses,
        document_count=len(documents),
        artifact_count=artifact_count,
        skill_count=skill_count,
        base_file_count=base_file_count,
        manifest_path=output_dir / "manifest.json",
    )


def normalize_output_dir(repo_root: Path, output_dir: Path | None) -> Path:
    build_root = (repo_root / "build").resolve()
    candidate = output_dir.resolve() if output_dir else build_root
    if candidate.is_relative_to(build_root):
        return candidate
    if candidate.exists():
        raise ValueError(f"output directory must stay within {build_root}")
    return candidate


def stage_output_dir(output_dir: Path) -> Path:
    ensure_dir(output_dir.parent)
    staging_dir = output_dir.parent / f".{output_dir.name}.tmp-{uuid4().hex}"
    staging_dir.mkdir(parents=True, exist_ok=False)
    return staging_dir


def render_for_harness(document: Document, harness: HarnessSpec, resolved: ResolvedModelConfig) -> Artifact | None:
    try:
        renderer = RENDERERS[harness.name]
    except KeyError as exc:
        raise ValueError(f"no renderer for harness {harness.name!r}") from exc
    return renderer(document, resolved, harness=harness)


def record_manifest_artifact(
    records: list[ManifestArtifact],
    *,
    repo_root: Path,
    harness: str,
    component: OutputComponent,
    relative_output_path: str,
    source_path: Path | None,
    kind: str,
    model_profile: str | None = None,
) -> None:
    if source_path is None:
        raise ValueError(f"missing source path for {relative_output_path}")
    records.append(
        ManifestArtifact(
            harness=harness,
            component=component,
            relative_output_path=relative_output_path,
            source_path=relative_to_root(source_path, repo_root),
            kind=kind,
            model_profile=model_profile,
        )
    )


def write_base_files(
    base_instructions: Path,
    output_dir: Path,
    harnesses: tuple[HarnessSpec, ...],
    repo_root: Path,
    manifest_records: list[ManifestArtifact],
) -> int:
    if not base_instructions.exists():
        return 0

    content = base_instructions.read_text()
    count = 0
    for harness in harnesses:
        relative_output_path = harness.base_output_path().as_posix()
        destination = output_dir / relative_output_path
        write_text(destination, content)
        record_manifest_artifact(
            manifest_records,
            repo_root=repo_root,
            harness=harness.name,
            component="base",
            relative_output_path=relative_output_path,
            source_path=base_instructions,
            kind="base",
        )
        count += 1
    return count


def copy_skills(
    skills_dir: Path,
    output_dir: Path,
    harnesses: tuple[HarnessSpec, ...],
    repo_root: Path,
    manifest_records: list[ManifestArtifact],
) -> int:
    if not skills_dir.exists():
        return 0

    count = 0
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith("."):
            continue
        for harness in harnesses:
            relative_output_path = harness.skill_output_path(skill_dir.name).as_posix()
            destination = output_dir / relative_output_path
            copy_dir(skill_dir, destination)
            record_manifest_artifact(
                manifest_records,
                repo_root=repo_root,
                harness=harness.name,
                component="skills",
                relative_output_path=relative_output_path,
                source_path=skill_dir,
                kind="skill",
            )
        count += 1
    return count


def write_manifest(
    repo_root: Path,
    build_output_dir: Path,
    environment: str,
    harnesses: tuple[HarnessSpec, ...],
    output_dir: Path,
    documents: list[Document],
    manifest_records: list[ManifestArtifact],
) -> Path:
    manifest = BuildManifest(
        schema_version=1,
        repo_root=str(repo_root),
        output_dir=str(build_output_dir),
        environment=environment,
        harnesses=tuple(spec.name for spec in harnesses),
        documents=tuple(relative_to_root(document.source_path, repo_root) for document in documents),
        artifacts=tuple(sorted(manifest_records, key=lambda artifact: (artifact.harness, artifact.component, artifact.relative_output_path))),
    )
    manifest_path = output_dir / "manifest.json"
    write_text(manifest_path, json.dumps(manifest.to_dict(), indent=2) + "\n")
    return manifest_path
