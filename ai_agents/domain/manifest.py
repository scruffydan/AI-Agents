from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from ai_agents.domain.harnesses import OutputComponent


@dataclass(frozen=True)
class ManifestArtifact:
    harness: str
    component: OutputComponent
    relative_output_path: str
    source_path: str
    kind: str
    model_profile: str | None = None


@dataclass(frozen=True)
class BuildManifest:
    schema_version: int
    repo_root: str
    output_dir: str
    environment: str
    harnesses: tuple[str, ...]
    documents: tuple[str, ...]
    artifacts: tuple[ManifestArtifact, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "repo_root": self.repo_root,
            "output_dir": self.output_dir,
            "environment": self.environment,
            "harnesses": list(self.harnesses),
            "documents": list(self.documents),
            "artifacts": [asdict(artifact) for artifact in self.artifacts],
        }


def relative_to_root(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()
