from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from ai_agents.content.loader import load_validated_documents
from ai_agents.domain.harnesses import all_harnesses
from ai_agents.profiles.resolver import load_model_profiles


@dataclass(frozen=True)
class DoctorIssue:
    scope: str
    message: str


@dataclass
class DoctorReport:
    repo_root: str
    checked: list[str] = field(default_factory=list)
    warnings: list[DoctorIssue] = field(default_factory=list)
    failures: list[DoctorIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failures

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo_root": self.repo_root,
            "checked": self.checked,
            "warnings": [asdict(issue) for issue in self.warnings],
            "failures": [asdict(issue) for issue in self.failures],
            "ok": self.ok,
        }


def run_doctor(repo_root: Path, *, verify_installed: bool, home_dir: Path | None = None) -> DoctorReport:
    repo_root = repo_root.resolve()
    report = DoctorReport(repo_root=str(repo_root))

    check_source(repo_root, report)
    check_build(repo_root, report)
    if verify_installed:
        check_installed(home_dir.resolve() if home_dir else Path.home(), report)

    return report


def check_source(repo_root: Path, report: DoctorReport) -> None:
    prompts_dir = repo_root / "source" / "prompts"
    profiles_path = repo_root / "source" / "model-profiles.toml"
    report.checked.append("source")

    try:
        load_validated_documents(prompts_dir, include_dir=prompts_dir)
        load_model_profiles(profiles_path)
    except Exception as exc:
        report.failures.append(DoctorIssue(scope="source", message=str(exc)))
        return

    for harness in all_harnesses():
        if not harness.install_entries:
            report.failures.append(DoctorIssue(scope="source", message=f"harness {harness.name} has no install entries"))


def check_build(repo_root: Path, report: DoctorReport) -> None:
    manifest_path = repo_root / "build" / "manifest.json"
    report.checked.append("build")

    if not manifest_path.exists():
        report.warnings.append(DoctorIssue(scope="build", message=f"build manifest not found: {manifest_path}"))
        return

    try:
        manifest = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as exc:
        report.failures.append(DoctorIssue(scope="build", message=f"invalid manifest JSON: {exc}"))
        return

    required_keys = {"schema_version", "repo_root", "output_dir", "environment", "harnesses", "documents", "artifacts"}
    missing = sorted(required_keys - set(manifest))
    if missing:
        report.failures.append(DoctorIssue(scope="build", message=f"manifest missing keys: {', '.join(missing)}"))
        return

    seen_paths: set[str] = set()
    for artifact in manifest["artifacts"]:
        relative_output_path = artifact["relative_output_path"]
        if relative_output_path in seen_paths:
            report.failures.append(DoctorIssue(scope="build", message=f"duplicate artifact path in manifest: {relative_output_path}"))
            continue
        seen_paths.add(relative_output_path)

        artifact_path = repo_root / "build" / Path(relative_output_path)
        if not artifact_path.exists():
            report.failures.append(DoctorIssue(scope="build", message=f"manifest references missing artifact: {relative_output_path}"))


def check_installed(home_dir: Path, report: DoctorReport) -> None:
    report.checked.append("installed")

    missing: list[str] = []
    for harness in all_harnesses():
        for entry in harness.install_entries:
            destination = home_dir / entry.destination
            if not destination.exists():
                missing.append(str(destination))

    if missing:
        preview = ", ".join(missing[:3])
        extra = len(missing) - min(len(missing), 3)
        suffix = f" (+{extra} more)" if extra else ""
        report.failures.append(DoctorIssue(scope="installed", message=f"missing installed targets: {preview}{suffix}"))


def render_doctor_report(report: DoctorReport) -> str:
    lines = [f"Repo root: {report.repo_root}", f"Checks: {', '.join(report.checked)}"]
    if report.warnings:
        lines.append(f"Warnings: {len(report.warnings)}")
        lines.extend(f"- [{issue.scope}] {issue.message}" for issue in report.warnings)
    if report.failures:
        lines.append(f"Failures: {len(report.failures)}")
        lines.extend(f"- [{issue.scope}] {issue.message}" for issue in report.failures)
    else:
        lines.append("Doctor passed")
    return "\n".join(lines)
