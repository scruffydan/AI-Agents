from __future__ import annotations

from pathlib import Path

from ai_agents.content.schema import parse_document
from ai_agents.domain.documents import Document


def load_documents(prompts_dir: Path, include_dir: Path | None = None) -> list[Document]:
    documents: list[Document] = []
    for path in sorted(prompts_dir.glob("*.md")):
        if path.name.startswith("_") or path.name == "AGENTS.md":
            continue
        documents.append(parse_document(path, include_dir=include_dir))
    return documents
