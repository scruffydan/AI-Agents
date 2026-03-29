from __future__ import annotations

from ai_agents.domain.documents import Document
from ai_agents.domain.harnesses import HarnessSpec, get_harness


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

        if document.kind.value == "mode" and not spec.supports_modes:
            raise ValueError(f"{document.source_path}: harness {harness_name!r} does not support modes")
