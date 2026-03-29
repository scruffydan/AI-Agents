from __future__ import annotations

from pathlib import Path

from ai_agents.content.schema import parse_document
from ai_agents.content.validation import validate_document
from ai_agents.domain.documents import Document
from ai_agents.domain.harnesses import HarnessSpec
from ai_agents.fs import ensure_no_symlinks


def load_documents(prompts_dir: Path, include_dir: Path | None = None) -> list[Document]:
    documents: list[Document] = []
    ensure_no_symlinks(prompts_dir)
    if include_dir is not None and include_dir != prompts_dir:
        ensure_no_symlinks(include_dir)
    for path in sorted(prompts_dir.glob("*.md")):
        if path.name.startswith("_") or path.name == "AGENTS.md":
            continue
        documents.append(parse_document(path, include_dir=include_dir))
    return documents


def load_validated_documents(
    prompts_dir: Path,
    include_dir: Path | None = None,
    harnesses: tuple[HarnessSpec, ...] | None = None,
) -> list[Document]:
    documents = load_documents(prompts_dir, include_dir=include_dir)
    for document in documents:
        validate_document(document, harnesses=harnesses)
    return documents
