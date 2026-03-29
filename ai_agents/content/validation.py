from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from ai_agents.domain.documents import Document
from ai_agents.domain.harnesses import HarnessSpec, get_harness


FORBIDDEN_SHARED_PATTERNS = (
    re.compile(r"@[a-zA-Z-]+"),
    re.compile(r"For Claude Code"),
    re.compile(r"For OpenCode"),
)


@dataclass(frozen=True)
class LintReport:
    checked_files: int
    violations: tuple[str, ...]


def validate_document(document: Document, harnesses: tuple[HarnessSpec, ...] | None = None) -> None:
    available = {spec.name: spec for spec in (harnesses or ())}

    if not document.targets:
        raise ValueError(f"{document.source_path}: document must define at least one target")

    for harness_name, override in document.targets.items():
        spec = available.get(harness_name) or get_harness(harness_name)

        if document.kind not in spec.supported_kinds:
            raise ValueError(
                f"{document.source_path}: harness {harness_name!r} does not support kind {document.kind.value!r}"
            )

        unsupported = sorted(set(override.metadata) - set(spec.supported_metadata_keys))
        if unsupported:
            names = ", ".join(unsupported)
            raise ValueError(
                f"{document.source_path}: harness {harness_name!r} does not support metadata keys: {names}"
            )

def lint_shared_content(repo_root: Path) -> LintReport:
    files = list((repo_root / "source" / "prompts").glob("*.md"))
    files.extend((repo_root / "source" / "skills").glob("**/*.md"))

    violations: list[str] = []
    for path in sorted(files):
        text = path.read_text()
        for pattern in FORBIDDEN_SHARED_PATTERNS:
            if pattern.search(text):
                violations.append(f"{path}: matches forbidden pattern {pattern.pattern!r}")
    return LintReport(checked_files=len(files), violations=tuple(violations))
